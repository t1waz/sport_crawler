import uuid

import grpc

from . import messages_pb2
from . import services_pb2_grpc


class WebsiteFetcherClient:
    def __init__(self, host: str, port: str) -> None:
        self._stub = services_pb2_grpc.WebsiteFetcherStub(
            channel=grpc.insecure_channel(f"{host}:{port}")
        )

    def fetch_page(self, url: str) -> str:
        request_id = str(uuid.uuid4())
        response = self._stub.fetch_page(
            messages_pb2.WebsiteFetchRequest(url=url, id=request_id)
        )

        assert response.id == request_id

        return response.content.decode()
