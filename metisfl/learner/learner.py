import cloudpickle
import gc
import queue
import os

import multiprocessing as mp
import metisfl.utils.proto_messages_factory as proto_factory

from inspect import signature
from pebble import ProcessPool
from metisfl.utils.metis_logger import MetisLogger
from metisfl.models.model_dataset import ModelDataset, ModelDatasetClassification, ModelDatasetRegression
from metisfl.learner.learner_evaluator import LearnerEvaluator
from metisfl.learner.learner_trainer import LearnerTrainer
from metisfl.utils.grpc_controller_client import GRPCControllerClient
from metisfl.utils.formatting import DictionaryFormatter
from metisfl.proto import learner_pb2, model_pb2, metis_pb2
from metisfl.encryption import fhe


class Learner(object):
    """
    Any invocation to the public functions of the Learner instance need to be wrapped inside a process,
    since the body of every function is generating a new Neural Network registry/context.

    In order to be able to run the training/evaluation/prediction functions as independent
    processes, we needed to create a ModelOperations class factory, depending on the neural network engine
    being used. For instance, for Keras we define the `_keras_model_ops_factory()` that internally imports
    the KerasModelOps class and for PyTorch we follow the same design by importing the PyTorchModeOps
    inside the body of the `_pytorch_model_ops_factory()` function.

    Specifically, no ModelOps subclass should be imported in the global scope of the learner but rather
    within the local scope (i.e., namespace) of each neural network model operations factory function.
    """

    def __init__(self,
                 learner_server_entity: metis_pb2.ServerEntity,
                 controller_server_entity: metis_pb2.ServerEntity,
                 he_scheme_config_pb: metis_pb2.HESchemeConfig,
                 nn_engine, model_dir,
                 train_dataset_fp, train_dataset_recipe_pkl,
                 validation_dataset_fp="", validation_dataset_recipe_pkl="",
                 test_dataset_fp="", test_dataset_recipe_pkl="",
                 recreate_queue_task_worker=False,
                 learner_credentials_fp="/tmp/metis/learner/"):
        self.learner_server_entity = learner_server_entity
        self._controller_server_entity = controller_server_entity
        self._he_scheme_config_pb = he_scheme_config_pb
        self._nn_engine = nn_engine
        self._model_dir = model_dir

        if not train_dataset_recipe_pkl:
            raise AssertionError("Training dataset recipe is required.")

        self.train_dataset_recipe_pkl, self.train_dataset_fp = \
            train_dataset_recipe_pkl, train_dataset_fp
        self.validation_dataset_recipe_pkl, self.validation_dataset_fp = \
            validation_dataset_recipe_pkl, validation_dataset_fp
        self.test_dataset_recipe_pkl, self.test_dataset_fp = \
            test_dataset_recipe_pkl, test_dataset_fp

        # We use pebble.ProcessPool() and not the native concurrent.futures.ProcessPoolExecutor() so that
        # when a termination signal (SIGTERM) is received we stop immediately the active task. This was
        # not possible with jobs/tasks submitted to the concurrent.futures.ProcessPoolExecutor()
        # because we had to wait for the active task to complete.
        # A single Process per training/evaluation/inference task.

        # If recreate_queue_task_worker is True, then we will create the entire model training backend
        # from scratch. For instance, in the case of Tensorflow, if this flag is True, then the
        # dependency graph holding the tensors and the variables definitions will be created again.
        # This re-creation adds substantial delay during model training and evaluation. If we do not
        # re-create, that is recreate_queue_task_worker is set to False, then we can re-use the existing
        # graph and avoid graph creation delays.
        # Unix default context is "fork", others: "spawn", "forkserver".
        # We use "spawn" because it initiates a new Python interpreter, and
        # it is more stable when running multiple processes in the same machine.
        self._mp_ctx = mp.get_context("spawn")
        worker_max_tasks = 0
        if recreate_queue_task_worker:
            worker_max_tasks = 1
        self._training_tasks_pool, self._training_tasks_futures_q = \
            ProcessPool(max_workers=1, max_tasks=worker_max_tasks, context=self._mp_ctx), \
                queue.Queue(maxsize=1)
        self._evaluation_tasks_pool, self._evaluation_tasks_futures_q = \
            ProcessPool(max_workers=1, max_tasks=worker_max_tasks, context=self._mp_ctx), \
                queue.Queue(maxsize=1)
        self._inference_tasks_pool, self._inference_tasks_futures_q = \
            ProcessPool(max_workers=1, max_tasks=worker_max_tasks, context=self._mp_ctx), \
                queue.Queue(maxsize=1)

        self._learner_controller_client = GRPCControllerClient(
            self._controller_server_entity,
            max_workers=1)
        # The `learner_id` param is generated by the controller with the join federation request
        # and it is used thereafter for every incoming/forwarding request.
        self.__learner_credentials_fp = learner_credentials_fp
        if not os.path.exists(self.__learner_credentials_fp):
            os.mkdir(self.__learner_credentials_fp)
        self.__learner_id = None
        self.__auth_token = None
        # TODO(stripeli): if we want to be more secure, we can dump an encrypted version of auth_token and learner_id
        self.__learner_id_fp = os.path.join(self.__learner_credentials_fp, "learner_id.txt")
        self.__auth_token_fp = os.path.join(self.__learner_credentials_fp, "auth_token.txt")

    def __getstate__(self):
        """
        Python needs to pickle the entire object, including its instance variables.
        Since one of these variables is the Pool object itself, the entire object cannot be pickled.
        We need to remove the Pool() variable from the object state in order to use the pool_task.
        The same holds for the gprc client, which underlying uses a futures thread pool.
        See also: https://stackoverflow.com/questions/25382455
        """
        self_dict = self.__dict__.copy()
        del self_dict['_training_tasks_pool']
        del self_dict['_training_tasks_futures_q']
        del self_dict['_evaluation_tasks_pool']
        del self_dict['_evaluation_tasks_futures_q']
        del self_dict['_inference_tasks_pool']
        del self_dict['_inference_tasks_futures_q']
        del self_dict['_learner_controller_client']
        return self_dict

    def _empty_tasks_q(self, future_tasks_q, forceful=False):
        while not future_tasks_q.empty():
            if forceful:
                # Forceful Shutdown. Non-blocking retrieval
                # of AsyncResult from futures queue.
                future_tasks_q.get(block=False).cancel()
            else:
                # Graceful Shutdown. Await for the underlying
                # future inside the queue to complete.
                future_tasks_q.get().result()

    def _create_model_dataset_helper(self, dataset_recipe_pkl, dataset_fp=None, default_class=None):
        # TODO(stripeli): Move into utils?
        """
        Thus function loads the dataset recipe dynamically. To achieve this, we
        need to see if the given recipe takes any arguments. The only argument
        we expect to be given is the path to the dataset (filepath).
        Therefore, we need to check the function's arguments
        cardinality if it is greater than 0.
        :param dataset_recipe_pkl:
        :param dataset_fp:
        :param default_class:
        :return:
        """

        if not dataset_recipe_pkl and not default_class:
            raise RuntimeError("Neither the dataset recipe or the default class are specified. Exiting ...")

        if dataset_recipe_pkl:
            dataset_recipe_fn = cloudpickle.load(open(dataset_recipe_pkl, "rb"))
            fn_params = signature(dataset_recipe_fn).parameters.keys()
            if len(fn_params) > 0:
                if dataset_fp:
                    # If the function expects an input we pass the dataset path.
                    dataset = dataset_recipe_fn(dataset_fp)
                else:
                    # If the dataset recipe requires an input file but none was given
                    # then we will return the default class.
                    dataset = default_class()
            else:
                # Else we just load the dataset as is.
                # This represents the in-memory dataset loading.
                dataset = dataset_recipe_fn()
        else:
            dataset = default_class()

        assert isinstance(dataset, ModelDataset), \
            "The dataset needs to be an instance of: {}".format(ModelDataset.__name__)
        return dataset

    def _load_model_datasets(self):
        train_dataset = self._create_model_dataset_helper(
            self.train_dataset_recipe_pkl, self.train_dataset_fp)
        validation_dataset = self._create_model_dataset_helper(
            self.validation_dataset_recipe_pkl, self.validation_dataset_fp,
            default_class=train_dataset.__class__)
        test_dataset = self._create_model_dataset_helper(
            self.test_dataset_recipe_pkl, self.test_dataset_fp,
            default_class=train_dataset.__class__)
        return train_dataset, validation_dataset, test_dataset

    def _load_model_datasets_size_specs_type_def(self):
        # Load only the dataset size, specifications and class type because
        # numpys or tf.tensors cannot be serialized and hence cannot be returned through the process.
        return [(d.get_size(), d.get_model_dataset_specifications(), type(d)) for d in self._load_model_datasets()]

    def _load_datasets_metadata_subproc(self):
        _generic_tasks_pool = ProcessPool(max_workers=1, max_tasks=1)
        datasets_specs_future = _generic_tasks_pool.schedule(function=self._load_model_datasets_size_specs_type_def)
        res = datasets_specs_future.result()
        _generic_tasks_pool.close()
        _generic_tasks_pool.join()
        return res

    def _mark_learning_task_completed(self, training_future):
        # If the returned future was completed successfully and was not cancelled,
        # meaning it did complete its running job, then notify the controller.
        if training_future.done() and not training_future.cancelled():
            completed_task_pb = training_future.result()
            self._learner_controller_client.mark_task_completed(
                learner_id=self.__learner_id,
                auth_token=self.__auth_token,
                completed_task_pb=completed_task_pb,
                block=False)

    def _model_ops_factory(self, nn_engine):
        if nn_engine == "keras":
            return self._model_ops_factory_keras
        if nn_engine == "pytorch":
            return self._model_ops_factory_pytorch

    def _model_ops_factory_keras(self, *args, **kwargs):
        from metisfl.models.keras.keras_model_ops import KerasModelOps
        he_scheme = None
        if self._he_scheme_config_pb.enabled:
            if self._he_scheme_config_pb.HasField("ckks_scheme_config"):
                he_scheme = fhe.CKKS(
                    self._he_scheme_config_pb.ckks_scheme_config.batch_size,
                    self._he_scheme_config_pb.ckks_scheme_config.scaling_factor_bits)
                he_scheme.load_crypto_context_from_file(
                    self._he_scheme_config_pb.crypto_context_file)
                he_scheme.load_public_key_from_file(
                    self._he_scheme_config_pb.public_key_file)
                he_scheme.load_private_key_from_file(
                    self._he_scheme_config_pb.private_key_file)
        model_ops = KerasModelOps(model_dir=self._model_dir, he_scheme=he_scheme, *args, **kwargs)
        return model_ops

    def _model_ops_factory_pytorch(self, *args, **kwargs):
        from metisfl.models.pytorch.pytorch_model_ops import PyTorchModelOps
        he_scheme = None
        if self._he_scheme_config_pb.enabled:
            if self._he_scheme_config_pb.HasField("ckks_scheme_config"):
                he_scheme = fhe.CKKS(
                    self._he_scheme_config_pb.ckks_scheme_config.batch_size,
                    self._he_scheme_config_pb.ckks_scheme_config.scaling_factor_bits)
                he_scheme.load_crypto_context_from_file(
                    self._he_scheme_config_pb.crypto_context_file)
                he_scheme.load_public_key_from_file(
                    self._he_scheme_config_pb.public_key_file)
                he_scheme.load_private_key_from_file(
                    self._he_scheme_config_pb.private_key_file)
        model_ops = PyTorchModelOps(model_dir=self._model_dir, he_scheme=he_scheme, *args, **kwargs)
        return model_ops

    def host_port_identifier(self):
        return "{}:{}".format(
            self.learner_server_entity.hostname,
            self.learner_server_entity.port)

    def join_federation(self):
        # FIXME(stripeli): If we create a learner controller instance
        #  once (without channel initialization) then the program hangs!
        train_dataset_meta, validation_dataset_meta, test_dataset_meta = self._load_datasets_metadata_subproc()
        is_classification = train_dataset_meta[2] == ModelDatasetClassification
        is_regression = train_dataset_meta[2] == ModelDatasetRegression

        self.__learner_id, self.__auth_token, status = \
            self._learner_controller_client.join_federation(self.learner_server_entity,
                                                            self.__learner_id_fp,
                                                            self.__auth_token_fp,
                                                            train_dataset_meta[0],
                                                            train_dataset_meta[1],
                                                            validation_dataset_meta[0],
                                                            validation_dataset_meta[1],
                                                            test_dataset_meta[0],
                                                            test_dataset_meta[1],
                                                            is_classification,
                                                            is_regression)
        return status

    def leave_federation(self):
        status = self._learner_controller_client.leave_federation(self.__learner_id, self.__auth_token, block=False)
        # Make sure that all pending tasks have been processed.
        self._learner_controller_client.shutdown()
        return status

    def model_evaluate(self, model_pb: model_pb2.Model, batch_size: int,
                       evaluation_datasets_pb: [learner_pb2.EvaluateModelRequest.dataset_to_eval],
                       metrics_pb: metis_pb2.EvaluationMetrics, verbose=False):
        MetisLogger.info("Learner {} starts model evaluation on requested datasets."
                         .format(self.host_port_identifier()))
        model_ops_fn = self._model_ops_factory(self._nn_engine)

        with LearnerEvaluator(model_ops_fn, model_pb) as learner_evaluator:
            # Invoke dataset recipes on a per model operations context,
            # since model evaluation will run as a subprocess.
            train_dataset, validation_dataset, test_dataset = self._load_model_datasets()
            # Need to unfold the pb into python list.
            metrics = [m for m in metrics_pb.metric]
            # Initialize to an empty metis_pb2.ModelEvaluation object all three variables.
            train_eval_pb = validation_eval_pb = test_eval_pb = metis_pb2.ModelEvaluation()
            for dataset_to_eval in evaluation_datasets_pb:
                if dataset_to_eval == learner_pb2.EvaluateModelRequest.dataset_to_eval.TRAINING:
                    train_eval_pb = learner_evaluator.evaluate_model(train_dataset, batch_size, metrics, verbose)
                if dataset_to_eval == learner_pb2.EvaluateModelRequest.dataset_to_eval.VALIDATION:
                    validation_eval_pb = learner_evaluator.evaluate_model(validation_dataset, batch_size, metrics, verbose)
                if dataset_to_eval == learner_pb2.EvaluateModelRequest.dataset_to_eval.TEST:
                    test_eval_pb = learner_evaluator.evaluate_model(test_dataset, batch_size, metrics, verbose)
            model_evaluations_pb = \
                proto_factory.MetisProtoMessages.construct_model_evaluations_pb(
                    training_evaluation_pb=train_eval_pb,
                    validation_evaluation_pb=validation_eval_pb,
                    test_evaluation_pb=test_eval_pb)
            MetisLogger.info("Learner {} completed model evaluation on requested datasets."
                             .format(self.host_port_identifier()))
        return model_evaluations_pb

    def model_infer(self, model_pb: model_pb2.Model, batch_size: int,
                    infer_train=False, infer_test=False, infer_valid=False, verbose=False):
        MetisLogger.info("Learner {} starts model inference on requested datasets."
                         .format(self.host_port_identifier()))
        # TODO(stripeli): infer model should behave similarly as the evaluate_model(), by looping over a
        #  similar learner_pb2.InferModelRequest.dataset_to_infer list.
        model_ops_fn = self._model_ops_factory(self._nn_engine)

        with LearnerEvaluator(model_ops_fn, model_pb) as learner_evaluator:
            # Invoke dataset recipes on a per model operations context,
            # since model inference will run as a subprocess.
            train_dataset, validation_dataset, test_dataset = self._load_model_datasets()
            inferred_res = {"train": None, "valid": None, "test": None}
            if infer_train:
                train_inferred = learner_evaluator.infer_model(train_dataset, batch_size, verbose)
                inferred_res["train"] = train_inferred
            if infer_valid:
                val_inferred = learner_evaluator.infer_model(validation_dataset, batch_size, verbose)
                inferred_res["valid"] = val_inferred
            if infer_test:
                test_inferred = learner_evaluator.infer_model(test_dataset, batch_size, verbose)
                inferred_res["test"] = test_inferred
            stringified_res = DictionaryFormatter.stringify(inferred_res, stringify_nan=True)
            MetisLogger.info("Learner {} completed model inference on requested datasets."
                             .format(self.host_port_identifier()))
        return stringified_res

    def model_train(self, learning_task_pb: metis_pb2.LearningTask,
                    hyperparameters_pb: metis_pb2.Hyperparameters, model_pb: model_pb2.Model,
                    verbose=False):
        MetisLogger.info("Learner {} starts model training on local training dataset."
                         .format(self.host_port_identifier()))
        model_ops_fn = self._model_ops_factory(self._nn_engine)

        # Invoke dataset recipes on a per model operations context,
        # since model training will run as a subprocess.
        with LearnerTrainer(model_ops_fn, model_pb) as learner_trainer:
            train_dataset, validation_dataset, test_dataset = self._load_model_datasets()
            completed_task_pb = learner_trainer.train_model(train_dataset, learning_task_pb,
                                                            hyperparameters_pb, validation_dataset,
                                                            test_dataset, verbose)
            MetisLogger.info("Learner {} completed model training on local training dataset."
                             .format(self.host_port_identifier()))
        return completed_task_pb

    def run_evaluation_task(self, model_pb: model_pb2.Model, batch_size: int,
                            evaluation_dataset_pb: [learner_pb2.EvaluateModelRequest.dataset_to_eval],
                            metrics_pb, cancel_running_tasks=False, block=False, verbose=False):
        # If `cancel_running_tasks` is True, we perform a forceful shutdown of running tasks, else graceful.
        self._empty_tasks_q(future_tasks_q=self._evaluation_tasks_futures_q, forceful=cancel_running_tasks)
        # If we submit the datasets and the metrics as is (i.e., as repeated fields) pickle cannot
        # serialize the repeated messages, and it requires converting the repeated messages into a list.
        evaluation_datasets_pb = [d for d in evaluation_dataset_pb]
        future = self._evaluation_tasks_pool.schedule(
            function=self.model_evaluate,
            args=[model_pb, batch_size, evaluation_datasets_pb, metrics_pb, verbose])
        self._evaluation_tasks_futures_q.put(future)
        model_evaluations_pb = metis_pb2.ModelEvaluations()
        if block:
            model_evaluations_pb = future.result()
        return model_evaluations_pb

    def run_inference_task(self):
        raise NotImplementedError("Not yet implemented.")

    def run_learning_task(self, learning_task_pb: metis_pb2.LearningTask,
                          hyperparameters_pb: metis_pb2.Hyperparameters, model_pb: model_pb2.Model,
                          cancel_running_tasks=False, block=False, verbose=False):
        # If `cancel_running_tasks` is True, we perform a forceful shutdown of running tasks, else graceful.
        self._empty_tasks_q(future_tasks_q=self._training_tasks_futures_q, forceful=cancel_running_tasks)
        # Submit the learning/training task to the Process Pool and add a callback to send the
        # trained local model to the controller when the learning task is complete. Given that
        # local training could span from seconds to hours, we cannot keep the grpc connection
        # open indefinitely and therefore the callback will collect the training result and
        # forward it accordingly to the controller.
        future = self._training_tasks_pool.schedule(
            function=self.model_train,
            args=[learning_task_pb, hyperparameters_pb, model_pb, verbose])
        # The following callback will trigger the request to the controller to receive the next task.
        future.add_done_callback(self._mark_learning_task_completed)
        self._training_tasks_futures_q.put(future)
        if block:
            future.result()
        # If the task is submitted for processing then it is not cancelled.
        is_task_submitted = not future.cancelled()
        return is_task_submitted

    def shutdown(self,
                 cancel_train_running_tasks=True,
                 cancel_eval_running_tasks=True,
                 cancel_infer_running_tasks=True):
        # If graceful is True, it will allow all pending tasks to be completed,
        # else it will stop immediately all active tasks. At first, we close the
        # tasks pool so that no more tasks can be submitted, and then we wait
        # gracefully or non-gracefully (cancel future) for their completion.
        self._training_tasks_pool.close()
        self._evaluation_tasks_pool.close()
        self._inference_tasks_pool.close()
        self._empty_tasks_q(self._training_tasks_futures_q, forceful=cancel_train_running_tasks)
        self._empty_tasks_q(self._evaluation_tasks_futures_q, forceful=cancel_eval_running_tasks)
        self._empty_tasks_q(self._inference_tasks_futures_q, forceful=cancel_infer_running_tasks)
        self._training_tasks_pool.join()
        self._evaluation_tasks_pool.join()
        self._inference_tasks_pool.join()
        gc.collect()
        # TODO(stripeli): we always return True, but we need to capture any failures that may occur while terminating.
        return True
