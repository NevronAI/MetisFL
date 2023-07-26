import copy
import itertools
import os

from metisfl.utils.logger import MetisLogger
from metisfl.utils.fedenv import FederationEnvironment


## TODO(@panoskyriakis): Check if correct given new environment
class EnvGen(object):

    def __init__(self, template_filepath: str):
        assert os.path.exists(template_filepath), \
            "Template file {} does not exist.".format(template_filepath)
        self.template_filepath = template_filepath
        if not template_filepath:
            self.template_filepath = os.path.join(
                os.path.dirname(__file__),
                "../config/template.yaml")

    def generate_localhost(self,
                           federation_rounds=10,
                           learners_num=10,
                           gpu_devices=[-1],
                           gpu_assignment="round_robin"):
        federation_environment = FederationEnvironment(self.template_filepath)
        federation_environment.federation_rounds \
            = federation_rounds
        learner_template = federation_environment.learners[0]
        federation_environment.learners = []
        gpu_devices_iter = itertools.cycle(gpu_devices)
        if gpu_assignment != "round_robin":
            MetisLogger.fatal("Only Round-Robin assignment is currently supported.")
        for k in range(learners_num):
            new_learner = copy.deepcopy(learner_template)
            new_learner.learner_id = "localhost:{}".format(k)
            new_learner.cuda_devices = [int(next(gpu_devices_iter))]
            new_learner.grpc_servicer.port = \
                int(learner_template.grpc_servicer.port + k)
            federation_environment.learners.append(new_learner)
        return federation_environment
