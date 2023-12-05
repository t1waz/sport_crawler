import asyncio

import grpc
from concurrent import futures
from common.grpc import services_pb2_grpc
from common.grpc import messages_pb2
from collector.services import StreamMaster
from redis import Redis

MAX_WORKERS = 5

SERVER_PORT = 55555
STREAM_KEY = "input_collector"


class WebsiteFetcherServicer(services_pb2_grpc.WebsiteFetcherServicer):
    def __init__(self, stream_master: StreamMaster, *args, **kwargs) -> None:
        self._stream_master = stream_master
        super().__init__(*args, **kwargs)

    def fetch_page(
        self, request: messages_pb2.WebsiteFetchRequest, context: grpc.ServicerContext
    ) -> messages_pb2.WebsiteFetchResponse:
        data = self._stream_master.get_data(data={"url": request.url})

        return messages_pb2.WebsiteFetchResponse(
            id=request.id, content=data["content"].encode()
        )


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=MAX_WORKERS))
    services_pb2_grpc.add_WebsiteFetcherServicer_to_server(
        WebsiteFetcherServicer(
            stream_master=StreamMaster(
                stream_key=STREAM_KEY, client=Redis(host="redis", port=6379)
            )
        ),
        server,
    )

    server.add_insecure_port(f"[::]:{SERVER_PORT}")
    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
