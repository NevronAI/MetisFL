import yaml
import re

from metisfl import config
from metisfl.proto import metis_pb2, model_pb2

from metisfl import config
from metisfl.encryption.encryption import Encryption
from metisfl.proto import metis_pb2
from metisfl.proto.proto_messages_factory import MetisProtoMessages
from metisfl.utils.metis_logger import MetisLogger
from .fedenv_schema import env_schema


class FederationEnvironment(object):

    def __init__(self, federation_environment_config_fp):
        fstream = open(federation_environment_config_fp).read()
        self._yaml = yaml.load(fstream, Loader=yaml.SafeLoader)
        env_schema.validate(self._yaml)
        self.controller = RemoteHost(self._yaml.get(
            "Controller"), enable_ssl=self.enable_ssl)
        self.learners = [RemoteHost(learner, enable_ssl=self.enable_ssl)
                         for learner in self._yaml.get("Learners")]
        self._setup_ssl()
        self._setup_encryption()

    def _setup_ssl(self):
        if self.enable_ssl:
            ssl_public_certificate = self._yaml.get("SSLPublicCertificate")
            ssl_private_key = self._yaml.get("SSLPrivateKey")
            if not ssl_public_certificate and not ssl_private_key:
                ssl_public_certificate, ssl_private_key = config.get_certificates()
                self._yaml["SSLPublicCertificate"] = ssl_public_certificate
                self._yaml["SSLPrivateKey"] = ssl_private_key
            elif ssl_public_certificate and ssl_private_key:
                return
            else:
                raise ValueError(
                    "Both SSL public certificate and private key must be provided.")

    def _setup_encryption(self):
        encryption_scheme = Encryption(self.he_scheme)
        initialized_params = encryption_scheme.initialize_crypto_params()
        for filename, location in initialized_params:
            self._yaml[filename] = location

    # Environment configuration
    @property
    def federation_rounds(self):
        return self._yaml.get("FederationRounds")

    @property
    def execution_time_cutoff_mins(self):
        return self._yaml.get("ExecutionCutoffTimeMins")

    @property
    def metric_cutoff_score(self):
        return self._yaml.get("EvaluationMetricCutoffScore")

    @property
    def communication_protocol(self):
        return self._yaml.get("CommunicationProtocol")

    @property
    def enable_ssl(self):
        return self._yaml.get("EnableSSL", False)

    @property
    def model_store(self):
        return self._yaml.get("ModelStore", "InMemory")

    @property
    def model_store_hostname(self):
        return self._yaml.get("ModelStoreHostname", None)

    @property
    def model_store_port(self):
        return self._yaml.get("ModelStorePort", None)

    @property
    def eviction_policy(self):
        return self._yaml.get("EvictionPolicy", "LineageLengthEviction")

    @property
    def lineage_length(self):
        return self._yaml.get("LineageLength", 1)

    # Homomorphic encryption configuration
    @property
    def he_scheme(self):
        return self._yaml.get("HEScheme")

    @property
    def he_batch_size(self):
        return self._yaml.get("HEBatchSize")

    @property
    def he_scaling_bits(self):
        return self._yaml.get("HEScalingBits")

    # Global training configuration
    @property
    def aggregation_rule(self):
        return self._yaml.get("AggregationRule")

    @property
    def participation_ratio(self):
        return self._yaml.get("ParticipationRatio")

    @property
    def scaling_factor(self):
        return self._yaml.get("ScalingFactor")

    @property
    def stride_length(self):
        return self._yaml.get("StrideLength")

    @property
    def particiapation_ratio(self):
        return self._yaml.get("ParticipationRatio", 1.0)

    # Local training configuration
    @property
    def train_batch_size(self):
        return self._yaml.get("BatchSize")

    @property
    def evaluation_metric(self):
        return self._yaml.get("EvaluationMetric")

    @property
    def local_epochs(self):
        return self._yaml.get("LocalEpochs")

    @property
    def validation_percentage(self):
        return self._yaml.get("ValidationPercentage")

    def get_local_model_config_pb(self):
        return MetisProtoMessages.construct_controller_modelhyperparams_pb(
            batch_size=self.train_batch_size,
            epochs=self.local_epochs,
            optimizer_pb=self._get_optimizer_pb(),
            percent_validation=self.validation_percentage)

    def _get_optimizer_pb(self):
        optimizer_name = self._yaml.get("Optimizer")
        params = self._yaml.get("OptimizerParams", {})
        new_params = {}
        for param_name, param_value in params.items():
            new_params[param_name] = str(param_value)
        return model_pb2.OptimizerConfig(name=optimizer_name, params=params)

    def get_global_model_config_pb(self):
        aggregation_rule_pb = MetisProtoMessages.construct_aggregation_rule_pb(
            rule_name=self.aggregation_rule,
            scaling_factor=self.scaling_factor,
            stride_length=self.stride_length,
            he_scheme_config_pb=self.get_he_scheme_pb(entity="controller"))
        return MetisProtoMessages.construct_global_model_specs(
            aggregation_rule_pb=aggregation_rule_pb,
            learners_participation_ratio=self.participation_ratio)

    # TODO(@stripeli): this does not make much sense in a realistic scenario.
    # the file paths here are local to each host, yet the pb constructed here is sent to the controller.
    def get_he_scheme_pb(self, entity: str) -> metis_pb2.HESchemeConfig:
        assert entity in ["controller", "learner"]
        if self.he_scheme == "CKKS":
            fhe_crypto_context_file = self._yaml["FHECryptoContextFile"]
            fhe_key_public_file = self._yaml["FHEPublicKeyFile"]
            fhe_key_private_file = self._yaml["FHEPrivateKeyFile"]
            return metis_pb2.HESchemeConfig(
                enabled=True,
                crypto_context_file=fhe_crypto_context_file,
                public_key_file=fhe_key_public_file if entity == "learner" else None,
                private_key_file=fhe_key_private_file if entity == "learner" else None,
                ckks_scheme_config=ckks_scheme_pb)
        else:
            MetisLogger.fatal("Not a supported homomorphic encryption scheme.")
            

    def get_communication_protocol_pb(self):
        # @stripeli clarify this
        protocol = self._yaml.get("CommunicationProtocol")
        semi_synchronous_lambda, semi_sync_recompute_num_updates = None, None
        if protocol == "SemiSynchronous":
            semi_synchronous_lambda = self._yaml.get(
                "SemiSynchronousLambda")
            semi_sync_recompute_num_updates = self._yaml.get(
                "SemiSynchronousRecomputeSteps")

        return MetisProtoMessages.construct_communication_specs_pb(
            protocol=self.communication_protocol,
            semi_sync_lambda=semi_synchronous_lambda,
            semi_sync_recompute_num_updates=semi_sync_recompute_num_updates)

    def get_model_store_config_pb(self):
        eviction_policy_pb = MetisProtoMessages.construct_eviction_policy_pb(
            self.eviction_policy, self.lineage_length)
        model_store_specs_pb = MetisProtoMessages.construct_model_store_specs_pb(
            eviction_policy_pb)
        if self.model_store.upper() == "INMEMORY":
            model_store_pb = metis_pb2.InMemoryStore(
                model_store_specs=model_store_specs_pb)
            return metis_pb2.ModelStoreConfig(in_memory_store=model_store_pb)
        elif self.model_store.upper() == "REDIS":
            server_entity_pb = MetisProtoMessages.construct_server_entity_pb(hostname=self.model_store_hostname,
                                                                             port=self.model_store_port)
            return metis_pb2.RedisDBStore(model_store_specs=model_store_specs_pb,
                                          server_entity=server_entity_pb)
        else:
            raise RuntimeError("Not a supported model store.")


class RemoteHost(object):
    def __init__(self, config_map, enable_ssl=False):
        self._config_map = config_map

    @property
    def id(self):
        return "{}:{}".format(self.grpc_hostname, self.grpc_port)

    @property
    def project_home(self):
        return self._config_map.get("ProjectHome")

    @property
    def hostname(self):
        return self._config_map.get("Hostname")

    @property
    def cuda_devices(self):
        return self._config_map.get("CudaDevices", None)

    @property
    def port(self):
        return self._config_map.get("Port", None)

    @property
    def username(self):
        return self._config_map.get("Username")

    @property
    def password(self):
        return self._config_map.get("Password")

    @property
    def key_filename(self):
        return self._config_map.get("KeyFilename")

    @property
    def passphrase(self):
        return self._config_map.get("Passphrase")

    @property
    def on_login_command(self):
        return self._config_map.get("OnLoginCommand")

    @property
    def grpc_hostname(self):
        return self._config_map.get("GRPCServicerHostname")

    @property
    def grpc_port(self):
        return self._config_map.get("GRPCServicerPort")

    @property
    def ssl_private_key(self):
        return self._config_map.get("SSLPrivateKey")

    @property
    def ssl_public_certificate(self):
        return self._config_map.get("SSLPublicCertificate")

    def get_fabric_connection_config(self):
        # Look for parameters values here:
        # https://docs.paramiko.org/en/latest/api/client.html#paramiko.client.SSHClient.connect
        # 'allow_agent' show be disabled if working with username/password.
        connect_kwargs = {
            "password": self.password,
            "allow_agent": False if self.password else True,
            "look_for_keys": True if self.key_filename else False,
        }
        if self.key_filename:
            connect_kwargs["key_filename"] = self.key_filename
            connect_kwargs["passphrase"] = self.passphrase

        conn_config = {
            "host": self.hostname,
            "port": self.port,
            "user": self.username,
            "connect_kwargs": connect_kwargs
        }
        return conn_config

    def get_server_entity_pb(self, gen_connection_entity=False) -> metis_pb2.ServerEntity:
        """Generate a ServerEntity proto object for the given parameters.

        Args:
            gen_connection_entity (bool, optional): Sets the private key to None. Defaults to False.

        Returns:
            metis_pb2.ServerEntity: The generated ServerEntity proto object.
        """
        private_key = self._config_map.get(
            "SSLPrivateKey") if not gen_connection_entity else None
        server_params_pb = metis_pb2.ServerEntity(
            hostname=self._config_map.get("GRPCServicerHostname"),
            port=self._config_map.get("GRPCServicerPort"),
            public_certificate_file=self._config_map.get(
                "SSLPublicCertificate"),
            private_key_file=private_key)

        return server_params_pb
