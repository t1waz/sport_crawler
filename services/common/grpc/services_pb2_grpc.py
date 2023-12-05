# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

from . import messages_pb2 as messages__pb2


class WebsiteFetcherStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.fetch_page = channel.unary_unary(
            "/WebsiteFetcher/fetch_page",
            request_serializer=messages__pb2.WebsiteFetchRequest.SerializeToString,
            response_deserializer=messages__pb2.WebsiteFetchResponse.FromString,
        )


class WebsiteFetcherServicer(object):
    """Missing associated documentation comment in .proto file."""

    def fetch_page(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details("Method not implemented!")
        raise NotImplementedError("Method not implemented!")


def add_WebsiteFetcherServicer_to_server(servicer, server):
    rpc_method_handlers = {
        "fetch_page": grpc.unary_unary_rpc_method_handler(
            servicer.fetch_page,
            request_deserializer=messages__pb2.WebsiteFetchRequest.FromString,
            response_serializer=messages__pb2.WebsiteFetchResponse.SerializeToString,
        ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
        "WebsiteFetcher", rpc_method_handlers
    )
    server.add_generic_rpc_handlers((generic_handler,))


# This class is part of an EXPERIMENTAL API.
class WebsiteFetcher(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def fetch_page(
        request,
        target,
        options=(),
        channel_credentials=None,
        call_credentials=None,
        insecure=False,
        compression=None,
        wait_for_ready=None,
        timeout=None,
        metadata=None,
    ):
        return grpc.experimental.unary_unary(
            request,
            target,
            "/WebsiteFetcher/fetch_page",
            messages__pb2.WebsiteFetchRequest.SerializeToString,
            messages__pb2.WebsiteFetchResponse.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
        )