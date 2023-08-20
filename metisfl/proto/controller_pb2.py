# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: metisfl/proto/controller.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from google.protobuf import timestamp_pb2 as google_dot_protobuf_dot_timestamp__pb2
from metisfl.proto import model_pb2 as metisfl_dot_proto_dot_model__pb2
from metisfl.proto import service_common_pb2 as metisfl_dot_proto_dot_service__common__pb2
from metisfl.proto import learner_pb2 as metisfl_dot_proto_dot_learner__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x1emetisfl/proto/controller.proto\x12\x07metisfl\x1a\x1fgoogle/protobuf/timestamp.proto\x1a\x19metisfl/proto/model.proto\x1a\"metisfl/proto/service_common.proto\x1a\x1bmetisfl/proto/learner.proto\"\xe7\x01\n\x11LearnerDescriptor\x12\x1a\n\x08hostname\x18\x01 \x01(\tR\x08hostname\x12\x12\n\x04port\x18\x02 \x01(\rR\x04port\x12\x34\n\x16root_certificate_bytes\x18\x03 \x01(\tR\x14rootCertificateBytes\x12\x38\n\x18public_certificate_bytes\x18\x04 \x01(\tR\x16publicCertificateBytes\x12\x32\n\x15num_training_examples\x18\x05 \x01(\rR\x13numTrainingExamples\"\x1b\n\tLearnerId\x12\x0e\n\x02id\x18\x01 \x01(\tR\x02id\"\xb0\x02\n\x10TrainDoneRequest\x12\x1d\n\nlearner_id\x18\x01 \x01(\tR\tlearnerId\x12\x1d\n\nauth_token\x18\x02 \x01(\tR\tauthToken\x12$\n\x05model\x18\x03 \x01(\x0b\x32\x0e.metisfl.ModelR\x05model\x12@\n\x07metrics\x18\x04 \x03(\x0b\x32&.metisfl.TrainDoneRequest.MetricsEntryR\x07metrics\x12:\n\x08metadata\x18\x05 \x01(\x0b\x32\x1e.metisfl.TaskExecutionMetadataR\x08metadata\x1a:\n\x0cMetricsEntry\x12\x10\n\x03key\x18\x01 \x01(\tR\x03key\x12\x14\n\x05value\x18\x02 \x01(\tR\x05value:\x02\x38\x01\"\xc3\x01\n\x14GetStatisticsRequest\x12\x46\n\x1f\x63ommunity_evaluation_backtracks\x18\x01 \x01(\x05R\x1d\x63ommunityEvaluationBacktracks\x12\x32\n\x15local_task_backtracks\x18\x02 \x01(\x05R\x13localTaskBacktracks\x12/\n\x13metadata_backtracks\x18\x03 \x01(\x05R\x12metadataBacktracks\"\xa9\x03\n\x15GetStatisticsResponse\x12\x1d\n\nlearner_id\x18\x01 \x03(\tR\tlearnerId\x12T\n\x14\x63ommunity_evaluation\x18\x02 \x03(\x0b\x32!.metisfl.CommunityModelEvaluationR\x13\x63ommunityEvaluation\x12U\n\rlearners_task\x18\x03 \x03(\x0b\x32\x30.metisfl.GetStatisticsResponse.LearnersTaskEntryR\x0clearnersTask\x12\x41\n\x08metadata\x18\x04 \x03(\x0b\x32%.metisfl.FederatedTaskRuntimeMetadataR\x08metadata\x12#\n\rjson_metadata\x18\x05 \x01(\tR\x0cjsonMetadata\x1a\\\n\x11LearnersTaskEntry\x12\x10\n\x03key\x18\x01 \x01(\tR\x03key\x12\x31\n\x05value\x18\x02 \x01(\x0b\x32\x1b.metisfl.LocalTasksMetadataR\x05value:\x02\x38\x01\"Y\n\x12LocalTasksMetadata\x12\x43\n\rtask_metadata\x18\x01 \x03(\x0b\x32\x1e.metisfl.TaskExecutionMetadataR\x0ctaskMetadata\"\xa7\x02\n\x15TaskExecutionMetadata\x12)\n\x10global_iteration\x18\x01 \x01(\rR\x0fglobalIteration\x12)\n\x10\x63ompleted_epochs\x18\x03 \x01(\x02R\x0f\x63ompletedEpochs\x12+\n\x11\x63ompleted_batches\x18\x04 \x01(\rR\x10\x63ompletedBatches\x12\x1d\n\nbatch_size\x18\x05 \x01(\rR\tbatchSize\x12\x35\n\x17processing_ms_per_epoch\x18\x06 \x01(\x02R\x14processingMsPerEpoch\x12\x35\n\x17processing_ms_per_batch\x18\x07 \x01(\x02R\x14processingMsPerBatch\"\xf6\x01\n\x18\x43ommunityModelEvaluation\x12)\n\x10global_iteration\x18\x01 \x01(\rR\x0fglobalIteration\x12T\n\x0b\x65valuations\x18\x02 \x03(\x0b\x32\x32.metisfl.CommunityModelEvaluation.EvaluationsEntryR\x0b\x65valuations\x1aY\n\x10\x45valuationsEntry\x12\x10\n\x03key\x18\x01 \x01(\tR\x03key\x12/\n\x05value\x18\x02 \x01(\x0b\x32\x19.metisfl.EvaluateResponseR\x05value:\x02\x38\x01\"\xf1\x10\n\x1c\x46\x65\x64\x65ratedTaskRuntimeMetadata\x12)\n\x10global_iteration\x18\x01 \x01(\rR\x0fglobalIteration\x12\x39\n\nstarted_at\x18\x02 \x01(\x0b\x32\x1a.google.protobuf.TimestampR\tstartedAt\x12=\n\x0c\x63ompleted_at\x18\x03 \x01(\x0b\x32\x1a.google.protobuf.TimestampR\x0b\x63ompletedAt\x12\x33\n\x16\x61ssigned_to_learner_id\x18\x04 \x03(\tR\x13\x61ssignedToLearnerId\x12\x35\n\x17\x63ompleted_by_learner_id\x18\x05 \x03(\tR\x14\x63ompletedByLearnerId\x12v\n\x17train_task_submitted_at\x18\x06 \x03(\x0b\x32?.metisfl.FederatedTaskRuntimeMetadata.TrainTaskSubmittedAtEntryR\x14trainTaskSubmittedAt\x12s\n\x16train_task_received_at\x18\x07 \x03(\x0b\x32>.metisfl.FederatedTaskRuntimeMetadata.TrainTaskReceivedAtEntryR\x13trainTaskReceivedAt\x12s\n\x16\x65val_task_submitted_at\x18\x08 \x03(\x0b\x32>.metisfl.FederatedTaskRuntimeMetadata.EvalTaskSubmittedAtEntryR\x13\x65valTaskSubmittedAt\x12p\n\x15\x65val_task_received_at\x18\t \x03(\x0b\x32=.metisfl.FederatedTaskRuntimeMetadata.EvalTaskReceivedAtEntryR\x12\x65valTaskReceivedAt\x12\x82\x01\n\x1bmodel_insertion_duration_ms\x18\n \x03(\x0b\x32\x43.metisfl.FederatedTaskRuntimeMetadata.ModelInsertionDurationMsEntryR\x18modelInsertionDurationMs\x12\x82\x01\n\x1bmodel_selection_duration_ms\x18\x0b \x03(\x0b\x32\x43.metisfl.FederatedTaskRuntimeMetadata.ModelSelectionDurationMsEntryR\x18modelSelectionDurationMs\x12[\n\x1cmodel_aggregation_started_at\x18\x0c \x01(\x0b\x32\x1a.google.protobuf.TimestampR\x19modelAggregationStartedAt\x12_\n\x1emodel_aggregation_completed_at\x18\r \x01(\x0b\x32\x1a.google.protobuf.TimestampR\x1bmodelAggregationCompletedAt\x12L\n#model_aggregation_total_duration_ms\x18\x0e \x01(\x01R\x1fmodelAggregationTotalDurationMs\x12?\n\x1cmodel_aggregation_block_size\x18\x0f \x03(\x01R\x19modelAggregationBlockSize\x12H\n!model_aggregation_block_memory_kb\x18\x10 \x03(\x01R\x1dmodelAggregationBlockMemoryKb\x12L\n#model_aggregation_block_duration_ms\x18\x11 \x03(\x01R\x1fmodelAggregationBlockDurationMs\x12S\n\x18model_tensor_quantifiers\x18\x12 \x03(\x0b\x32\x19.metisfl.TensorQuantifierR\x16modelTensorQuantifiers\x1a\x63\n\x19TrainTaskSubmittedAtEntry\x12\x10\n\x03key\x18\x01 \x01(\tR\x03key\x12\x30\n\x05value\x18\x02 \x01(\x0b\x32\x1a.google.protobuf.TimestampR\x05value:\x02\x38\x01\x1a\x62\n\x18TrainTaskReceivedAtEntry\x12\x10\n\x03key\x18\x01 \x01(\tR\x03key\x12\x30\n\x05value\x18\x02 \x01(\x0b\x32\x1a.google.protobuf.TimestampR\x05value:\x02\x38\x01\x1a\x62\n\x18\x45valTaskSubmittedAtEntry\x12\x10\n\x03key\x18\x01 \x01(\tR\x03key\x12\x30\n\x05value\x18\x02 \x01(\x0b\x32\x1a.google.protobuf.TimestampR\x05value:\x02\x38\x01\x1a\x61\n\x17\x45valTaskReceivedAtEntry\x12\x10\n\x03key\x18\x01 \x01(\tR\x03key\x12\x30\n\x05value\x18\x02 \x01(\x0b\x32\x1a.google.protobuf.TimestampR\x05value:\x02\x38\x01\x1aK\n\x1dModelInsertionDurationMsEntry\x12\x10\n\x03key\x18\x01 \x01(\tR\x03key\x12\x14\n\x05value\x18\x02 \x01(\x01R\x05value:\x02\x38\x01\x1aK\n\x1dModelSelectionDurationMsEntry\x12\x10\n\x03key\x18\x01 \x01(\tR\x03key\x12\x14\n\x05value\x18\x02 \x01(\x01R\x05value:\x02\x38\x01\x32\xdb\x03\n\x11\x43ontrollerService\x12\x31\n\x0fGetHealthStatus\x12\x0e.metisfl.Empty\x1a\x0c.metisfl.Ack\"\x00\x12\x31\n\x0fSetInitialModel\x12\x0e.metisfl.Model\x1a\x0c.metisfl.Ack\"\x00\x12\x42\n\x0eJoinFederation\x12\x1a.metisfl.LearnerDescriptor\x1a\x12.metisfl.LearnerId\"\x00\x12\x35\n\x0fLeaveFederation\x12\x12.metisfl.LearnerId\x1a\x0c.metisfl.Ack\"\x00\x12/\n\rStartTraining\x12\x0e.metisfl.Empty\x1a\x0c.metisfl.Ack\"\x00\x12\x36\n\tTrainDone\x12\x19.metisfl.TrainDoneRequest\x1a\x0c.metisfl.Ack\"\x00\x12P\n\rGetStatistics\x12\x1d.metisfl.GetStatisticsRequest\x1a\x1e.metisfl.GetStatisticsResponse\"\x00\x12*\n\x08ShutDown\x12\x0e.metisfl.Empty\x1a\x0c.metisfl.Ack\"\x00\x62\x06proto3')



_LEARNERDESCRIPTOR = DESCRIPTOR.message_types_by_name['LearnerDescriptor']
_LEARNERID = DESCRIPTOR.message_types_by_name['LearnerId']
_TRAINDONEREQUEST = DESCRIPTOR.message_types_by_name['TrainDoneRequest']
_TRAINDONEREQUEST_METRICSENTRY = _TRAINDONEREQUEST.nested_types_by_name['MetricsEntry']
_GETSTATISTICSREQUEST = DESCRIPTOR.message_types_by_name['GetStatisticsRequest']
_GETSTATISTICSRESPONSE = DESCRIPTOR.message_types_by_name['GetStatisticsResponse']
_GETSTATISTICSRESPONSE_LEARNERSTASKENTRY = _GETSTATISTICSRESPONSE.nested_types_by_name['LearnersTaskEntry']
_LOCALTASKSMETADATA = DESCRIPTOR.message_types_by_name['LocalTasksMetadata']
_TASKEXECUTIONMETADATA = DESCRIPTOR.message_types_by_name['TaskExecutionMetadata']
_COMMUNITYMODELEVALUATION = DESCRIPTOR.message_types_by_name['CommunityModelEvaluation']
_COMMUNITYMODELEVALUATION_EVALUATIONSENTRY = _COMMUNITYMODELEVALUATION.nested_types_by_name['EvaluationsEntry']
_FEDERATEDTASKRUNTIMEMETADATA = DESCRIPTOR.message_types_by_name['FederatedTaskRuntimeMetadata']
_FEDERATEDTASKRUNTIMEMETADATA_TRAINTASKSUBMITTEDATENTRY = _FEDERATEDTASKRUNTIMEMETADATA.nested_types_by_name['TrainTaskSubmittedAtEntry']
_FEDERATEDTASKRUNTIMEMETADATA_TRAINTASKRECEIVEDATENTRY = _FEDERATEDTASKRUNTIMEMETADATA.nested_types_by_name['TrainTaskReceivedAtEntry']
_FEDERATEDTASKRUNTIMEMETADATA_EVALTASKSUBMITTEDATENTRY = _FEDERATEDTASKRUNTIMEMETADATA.nested_types_by_name['EvalTaskSubmittedAtEntry']
_FEDERATEDTASKRUNTIMEMETADATA_EVALTASKRECEIVEDATENTRY = _FEDERATEDTASKRUNTIMEMETADATA.nested_types_by_name['EvalTaskReceivedAtEntry']
_FEDERATEDTASKRUNTIMEMETADATA_MODELINSERTIONDURATIONMSENTRY = _FEDERATEDTASKRUNTIMEMETADATA.nested_types_by_name['ModelInsertionDurationMsEntry']
_FEDERATEDTASKRUNTIMEMETADATA_MODELSELECTIONDURATIONMSENTRY = _FEDERATEDTASKRUNTIMEMETADATA.nested_types_by_name['ModelSelectionDurationMsEntry']
LearnerDescriptor = _reflection.GeneratedProtocolMessageType('LearnerDescriptor', (_message.Message,), {
  'DESCRIPTOR' : _LEARNERDESCRIPTOR,
  '__module__' : 'metisfl.proto.controller_pb2'
  # @@protoc_insertion_point(class_scope:metisfl.LearnerDescriptor)
  })
_sym_db.RegisterMessage(LearnerDescriptor)

LearnerId = _reflection.GeneratedProtocolMessageType('LearnerId', (_message.Message,), {
  'DESCRIPTOR' : _LEARNERID,
  '__module__' : 'metisfl.proto.controller_pb2'
  # @@protoc_insertion_point(class_scope:metisfl.LearnerId)
  })
_sym_db.RegisterMessage(LearnerId)

TrainDoneRequest = _reflection.GeneratedProtocolMessageType('TrainDoneRequest', (_message.Message,), {

  'MetricsEntry' : _reflection.GeneratedProtocolMessageType('MetricsEntry', (_message.Message,), {
    'DESCRIPTOR' : _TRAINDONEREQUEST_METRICSENTRY,
    '__module__' : 'metisfl.proto.controller_pb2'
    # @@protoc_insertion_point(class_scope:metisfl.TrainDoneRequest.MetricsEntry)
    })
  ,
  'DESCRIPTOR' : _TRAINDONEREQUEST,
  '__module__' : 'metisfl.proto.controller_pb2'
  # @@protoc_insertion_point(class_scope:metisfl.TrainDoneRequest)
  })
_sym_db.RegisterMessage(TrainDoneRequest)
_sym_db.RegisterMessage(TrainDoneRequest.MetricsEntry)

GetStatisticsRequest = _reflection.GeneratedProtocolMessageType('GetStatisticsRequest', (_message.Message,), {
  'DESCRIPTOR' : _GETSTATISTICSREQUEST,
  '__module__' : 'metisfl.proto.controller_pb2'
  # @@protoc_insertion_point(class_scope:metisfl.GetStatisticsRequest)
  })
_sym_db.RegisterMessage(GetStatisticsRequest)

GetStatisticsResponse = _reflection.GeneratedProtocolMessageType('GetStatisticsResponse', (_message.Message,), {

  'LearnersTaskEntry' : _reflection.GeneratedProtocolMessageType('LearnersTaskEntry', (_message.Message,), {
    'DESCRIPTOR' : _GETSTATISTICSRESPONSE_LEARNERSTASKENTRY,
    '__module__' : 'metisfl.proto.controller_pb2'
    # @@protoc_insertion_point(class_scope:metisfl.GetStatisticsResponse.LearnersTaskEntry)
    })
  ,
  'DESCRIPTOR' : _GETSTATISTICSRESPONSE,
  '__module__' : 'metisfl.proto.controller_pb2'
  # @@protoc_insertion_point(class_scope:metisfl.GetStatisticsResponse)
  })
_sym_db.RegisterMessage(GetStatisticsResponse)
_sym_db.RegisterMessage(GetStatisticsResponse.LearnersTaskEntry)

LocalTasksMetadata = _reflection.GeneratedProtocolMessageType('LocalTasksMetadata', (_message.Message,), {
  'DESCRIPTOR' : _LOCALTASKSMETADATA,
  '__module__' : 'metisfl.proto.controller_pb2'
  # @@protoc_insertion_point(class_scope:metisfl.LocalTasksMetadata)
  })
_sym_db.RegisterMessage(LocalTasksMetadata)

TaskExecutionMetadata = _reflection.GeneratedProtocolMessageType('TaskExecutionMetadata', (_message.Message,), {
  'DESCRIPTOR' : _TASKEXECUTIONMETADATA,
  '__module__' : 'metisfl.proto.controller_pb2'
  # @@protoc_insertion_point(class_scope:metisfl.TaskExecutionMetadata)
  })
_sym_db.RegisterMessage(TaskExecutionMetadata)

CommunityModelEvaluation = _reflection.GeneratedProtocolMessageType('CommunityModelEvaluation', (_message.Message,), {

  'EvaluationsEntry' : _reflection.GeneratedProtocolMessageType('EvaluationsEntry', (_message.Message,), {
    'DESCRIPTOR' : _COMMUNITYMODELEVALUATION_EVALUATIONSENTRY,
    '__module__' : 'metisfl.proto.controller_pb2'
    # @@protoc_insertion_point(class_scope:metisfl.CommunityModelEvaluation.EvaluationsEntry)
    })
  ,
  'DESCRIPTOR' : _COMMUNITYMODELEVALUATION,
  '__module__' : 'metisfl.proto.controller_pb2'
  # @@protoc_insertion_point(class_scope:metisfl.CommunityModelEvaluation)
  })
_sym_db.RegisterMessage(CommunityModelEvaluation)
_sym_db.RegisterMessage(CommunityModelEvaluation.EvaluationsEntry)

FederatedTaskRuntimeMetadata = _reflection.GeneratedProtocolMessageType('FederatedTaskRuntimeMetadata', (_message.Message,), {

  'TrainTaskSubmittedAtEntry' : _reflection.GeneratedProtocolMessageType('TrainTaskSubmittedAtEntry', (_message.Message,), {
    'DESCRIPTOR' : _FEDERATEDTASKRUNTIMEMETADATA_TRAINTASKSUBMITTEDATENTRY,
    '__module__' : 'metisfl.proto.controller_pb2'
    # @@protoc_insertion_point(class_scope:metisfl.FederatedTaskRuntimeMetadata.TrainTaskSubmittedAtEntry)
    })
  ,

  'TrainTaskReceivedAtEntry' : _reflection.GeneratedProtocolMessageType('TrainTaskReceivedAtEntry', (_message.Message,), {
    'DESCRIPTOR' : _FEDERATEDTASKRUNTIMEMETADATA_TRAINTASKRECEIVEDATENTRY,
    '__module__' : 'metisfl.proto.controller_pb2'
    # @@protoc_insertion_point(class_scope:metisfl.FederatedTaskRuntimeMetadata.TrainTaskReceivedAtEntry)
    })
  ,

  'EvalTaskSubmittedAtEntry' : _reflection.GeneratedProtocolMessageType('EvalTaskSubmittedAtEntry', (_message.Message,), {
    'DESCRIPTOR' : _FEDERATEDTASKRUNTIMEMETADATA_EVALTASKSUBMITTEDATENTRY,
    '__module__' : 'metisfl.proto.controller_pb2'
    # @@protoc_insertion_point(class_scope:metisfl.FederatedTaskRuntimeMetadata.EvalTaskSubmittedAtEntry)
    })
  ,

  'EvalTaskReceivedAtEntry' : _reflection.GeneratedProtocolMessageType('EvalTaskReceivedAtEntry', (_message.Message,), {
    'DESCRIPTOR' : _FEDERATEDTASKRUNTIMEMETADATA_EVALTASKRECEIVEDATENTRY,
    '__module__' : 'metisfl.proto.controller_pb2'
    # @@protoc_insertion_point(class_scope:metisfl.FederatedTaskRuntimeMetadata.EvalTaskReceivedAtEntry)
    })
  ,

  'ModelInsertionDurationMsEntry' : _reflection.GeneratedProtocolMessageType('ModelInsertionDurationMsEntry', (_message.Message,), {
    'DESCRIPTOR' : _FEDERATEDTASKRUNTIMEMETADATA_MODELINSERTIONDURATIONMSENTRY,
    '__module__' : 'metisfl.proto.controller_pb2'
    # @@protoc_insertion_point(class_scope:metisfl.FederatedTaskRuntimeMetadata.ModelInsertionDurationMsEntry)
    })
  ,

  'ModelSelectionDurationMsEntry' : _reflection.GeneratedProtocolMessageType('ModelSelectionDurationMsEntry', (_message.Message,), {
    'DESCRIPTOR' : _FEDERATEDTASKRUNTIMEMETADATA_MODELSELECTIONDURATIONMSENTRY,
    '__module__' : 'metisfl.proto.controller_pb2'
    # @@protoc_insertion_point(class_scope:metisfl.FederatedTaskRuntimeMetadata.ModelSelectionDurationMsEntry)
    })
  ,
  'DESCRIPTOR' : _FEDERATEDTASKRUNTIMEMETADATA,
  '__module__' : 'metisfl.proto.controller_pb2'
  # @@protoc_insertion_point(class_scope:metisfl.FederatedTaskRuntimeMetadata)
  })
_sym_db.RegisterMessage(FederatedTaskRuntimeMetadata)
_sym_db.RegisterMessage(FederatedTaskRuntimeMetadata.TrainTaskSubmittedAtEntry)
_sym_db.RegisterMessage(FederatedTaskRuntimeMetadata.TrainTaskReceivedAtEntry)
_sym_db.RegisterMessage(FederatedTaskRuntimeMetadata.EvalTaskSubmittedAtEntry)
_sym_db.RegisterMessage(FederatedTaskRuntimeMetadata.EvalTaskReceivedAtEntry)
_sym_db.RegisterMessage(FederatedTaskRuntimeMetadata.ModelInsertionDurationMsEntry)
_sym_db.RegisterMessage(FederatedTaskRuntimeMetadata.ModelSelectionDurationMsEntry)

_CONTROLLERSERVICE = DESCRIPTOR.services_by_name['ControllerService']
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  _TRAINDONEREQUEST_METRICSENTRY._options = None
  _TRAINDONEREQUEST_METRICSENTRY._serialized_options = b'8\001'
  _GETSTATISTICSRESPONSE_LEARNERSTASKENTRY._options = None
  _GETSTATISTICSRESPONSE_LEARNERSTASKENTRY._serialized_options = b'8\001'
  _COMMUNITYMODELEVALUATION_EVALUATIONSENTRY._options = None
  _COMMUNITYMODELEVALUATION_EVALUATIONSENTRY._serialized_options = b'8\001'
  _FEDERATEDTASKRUNTIMEMETADATA_TRAINTASKSUBMITTEDATENTRY._options = None
  _FEDERATEDTASKRUNTIMEMETADATA_TRAINTASKSUBMITTEDATENTRY._serialized_options = b'8\001'
  _FEDERATEDTASKRUNTIMEMETADATA_TRAINTASKRECEIVEDATENTRY._options = None
  _FEDERATEDTASKRUNTIMEMETADATA_TRAINTASKRECEIVEDATENTRY._serialized_options = b'8\001'
  _FEDERATEDTASKRUNTIMEMETADATA_EVALTASKSUBMITTEDATENTRY._options = None
  _FEDERATEDTASKRUNTIMEMETADATA_EVALTASKSUBMITTEDATENTRY._serialized_options = b'8\001'
  _FEDERATEDTASKRUNTIMEMETADATA_EVALTASKRECEIVEDATENTRY._options = None
  _FEDERATEDTASKRUNTIMEMETADATA_EVALTASKRECEIVEDATENTRY._serialized_options = b'8\001'
  _FEDERATEDTASKRUNTIMEMETADATA_MODELINSERTIONDURATIONMSENTRY._options = None
  _FEDERATEDTASKRUNTIMEMETADATA_MODELINSERTIONDURATIONMSENTRY._serialized_options = b'8\001'
  _FEDERATEDTASKRUNTIMEMETADATA_MODELSELECTIONDURATIONMSENTRY._options = None
  _FEDERATEDTASKRUNTIMEMETADATA_MODELSELECTIONDURATIONMSENTRY._serialized_options = b'8\001'
  _LEARNERDESCRIPTOR._serialized_start=169
  _LEARNERDESCRIPTOR._serialized_end=400
  _LEARNERID._serialized_start=402
  _LEARNERID._serialized_end=429
  _TRAINDONEREQUEST._serialized_start=432
  _TRAINDONEREQUEST._serialized_end=736
  _TRAINDONEREQUEST_METRICSENTRY._serialized_start=678
  _TRAINDONEREQUEST_METRICSENTRY._serialized_end=736
  _GETSTATISTICSREQUEST._serialized_start=739
  _GETSTATISTICSREQUEST._serialized_end=934
  _GETSTATISTICSRESPONSE._serialized_start=937
  _GETSTATISTICSRESPONSE._serialized_end=1362
  _GETSTATISTICSRESPONSE_LEARNERSTASKENTRY._serialized_start=1270
  _GETSTATISTICSRESPONSE_LEARNERSTASKENTRY._serialized_end=1362
  _LOCALTASKSMETADATA._serialized_start=1364
  _LOCALTASKSMETADATA._serialized_end=1453
  _TASKEXECUTIONMETADATA._serialized_start=1456
  _TASKEXECUTIONMETADATA._serialized_end=1751
  _COMMUNITYMODELEVALUATION._serialized_start=1754
  _COMMUNITYMODELEVALUATION._serialized_end=2000
  _COMMUNITYMODELEVALUATION_EVALUATIONSENTRY._serialized_start=1911
  _COMMUNITYMODELEVALUATION_EVALUATIONSENTRY._serialized_end=2000
  _FEDERATEDTASKRUNTIMEMETADATA._serialized_start=2003
  _FEDERATEDTASKRUNTIMEMETADATA._serialized_end=4164
  _FEDERATEDTASKRUNTIMEMETADATA_TRAINTASKSUBMITTEDATENTRY._serialized_start=3612
  _FEDERATEDTASKRUNTIMEMETADATA_TRAINTASKSUBMITTEDATENTRY._serialized_end=3711
  _FEDERATEDTASKRUNTIMEMETADATA_TRAINTASKRECEIVEDATENTRY._serialized_start=3713
  _FEDERATEDTASKRUNTIMEMETADATA_TRAINTASKRECEIVEDATENTRY._serialized_end=3811
  _FEDERATEDTASKRUNTIMEMETADATA_EVALTASKSUBMITTEDATENTRY._serialized_start=3813
  _FEDERATEDTASKRUNTIMEMETADATA_EVALTASKSUBMITTEDATENTRY._serialized_end=3911
  _FEDERATEDTASKRUNTIMEMETADATA_EVALTASKRECEIVEDATENTRY._serialized_start=3913
  _FEDERATEDTASKRUNTIMEMETADATA_EVALTASKRECEIVEDATENTRY._serialized_end=4010
  _FEDERATEDTASKRUNTIMEMETADATA_MODELINSERTIONDURATIONMSENTRY._serialized_start=4012
  _FEDERATEDTASKRUNTIMEMETADATA_MODELINSERTIONDURATIONMSENTRY._serialized_end=4087
  _FEDERATEDTASKRUNTIMEMETADATA_MODELSELECTIONDURATIONMSENTRY._serialized_start=4089
  _FEDERATEDTASKRUNTIMEMETADATA_MODELSELECTIONDURATIONMSENTRY._serialized_end=4164
  _CONTROLLERSERVICE._serialized_start=4167
  _CONTROLLERSERVICE._serialized_end=4642
# @@protoc_insertion_point(module_scope)
