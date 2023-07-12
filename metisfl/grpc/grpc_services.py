import queue
import time
from concurrent import futures

import grpc
from grpc._cython import cygrpc
from pebble import ThreadPool
from metisfl.proto import controller_pb2_grpc, service_common_pb2

from metisfl.proto.metis_pb2 import ServerEntity
from metisfl.utils.metis_logger import MetisLogger
from metisfl.utils.ssl_configurator import SSLConfigurator


class GRPCEndpoint(object):

    def __init__(self, server_entity: ServerEntity):
        self.server_entity = server_entity
        self.listening_endpoint = "{}:{}".format(
            server_entity.hostname,
            server_entity.port)


class GRPCChannelMaxMsgLength(object):

    def __init__(self, server_entity: ServerEntity):
        self.grpc_endpoint = GRPCEndpoint(server_entity)
        # TODO(stripeli): Remove this. Extend Channel class to read messages as chunks
        #  similar to this, C++: https://jbrandhorst.com/post/grpc-binary-blob-stream/
        self.channel_options = \
            [(cygrpc.ChannelArgKey.max_send_message_length, -1),
             (cygrpc.ChannelArgKey.max_receive_message_length, -1)]

        public_certificate, _ = SSLConfigurator().load_certificates_from_ssl_config_pb(
            ssl_config_pb=server_entity.ssl_config, as_stream=True)
        if public_certificate:
            ssl_credentials = grpc.ssl_channel_credentials(public_certificate)
            self.channel = grpc.secure_channel(
                target=self.grpc_endpoint.listening_endpoint,
                options=self.channel_options,
                credentials=ssl_credentials)
        else:
            self.channel = grpc.insecure_channel(
                target=self.grpc_endpoint.listening_endpoint,
                options=self.channel_options)


class GRPCClient(object):

    def __init__(self, server_entity: ServerEntity, max_workers=1):
        self.grpc_endpoint = GRPCEndpoint(server_entity)
        self.executor = ThreadPool(max_workers=max_workers)
        self.executor_pool = queue.Queue()
        self._channel = GRPCChannelMaxMsgLength(self.grpc_endpoint.server_entity).channel
        self._stub = controller_pb2_grpc.ControllerServiceStub(self._channel)


    def check_health_status(self, request_retries=1, request_timeout=None, block=True):
        def _request(_timeout=None):
            get_services_health_status_request_pb = service_common_pb2.GetServicesHealthStatusRequest()
            MetisLogger.info("Requesting controller's health status.")
            response = self._stub.GetServicesHealthStatus(get_services_health_status_request_pb, timeout=_timeout)
            MetisLogger.info("Received controller's health status, {} - {}".format(
                self.grpc_endpoint.listening_endpoint, response))
            return response
        return self.schedule_request(_request, request_retries, request_timeout, block)


    def schedule_request(self, request, request_retries=1, request_timeout=None, block=True):
        if request_retries > 1:
            future = self.executor.schedule(function=self._request_with_timeout,
                                            args=(request, request_timeout, request_retries))
        else:
            future = self.executor.schedule(request)

        if block:
            return future.result()
        else:
            self.executor_pool.put(future)

    def shutdown(self):
        self.executor.close()
        self.executor.join()
        self._channel.close()

    def _request_with_timeout(self, request_fn, request_timeout, request_retries):
        count_retries = 0
        response = None
        while count_retries < request_retries:
            try:
                response = request_fn(request_timeout)
            except grpc.RpcError as rpc_error:
                MetisLogger.info("Exception Raised: {}, Retrying...".format(rpc_error))
                if rpc_error.code() == grpc.StatusCode.UNAVAILABLE:
                    time.sleep(10)  # sleep for 10secs in-between requests if server is Unavailable.
            else:
                break
            count_retries += 1
        return response       


class GRPCServerMaxMsgLength(object):

    def __init__(self, max_workers=None, server_entity: ServerEntity = None):
        self.grpc_endpoint = GRPCEndpoint(server_entity)

        # TODO(stripeli): Remove this. Extend Channel class to read messages as chunks
        #  similar to this, C++: https://jbrandhorst.com/post/grpc-binary-blob-stream/
        # (cygrpc.ChannelArgKey.max_concurrent_streams, 1000),
        # (grpc.chttp2.lookahead_bytes, 1024),
        # (grpc.chttp2.max_frame_size, 16777215)]
        self.channel_options = \
            [(cygrpc.ChannelArgKey.max_send_message_length, -1),
             (cygrpc.ChannelArgKey.max_receive_message_length, -1), ]
        self.executor = futures.ThreadPoolExecutor(max_workers=max_workers)
        self.server = grpc.server(self.executor, options=self.channel_options)

        public_certificate, private_key = SSLConfigurator().load_certificates_from_ssl_config_pb(
            ssl_config_pb=server_entity.ssl_config, as_stream=True)
        if public_certificate and private_key:
            server_credentials = grpc.ssl_server_credentials((
                (private_key, public_certificate, ),
            ))
            self.server.add_secure_port(
                self.grpc_endpoint.listening_endpoint,
                server_credentials)
        else:
            self.server.add_insecure_port(
                self.grpc_endpoint.listening_endpoint)
