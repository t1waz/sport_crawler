from common.grpc.clients import WebsiteFetcherClient


def get_website_fetcher_client() -> WebsiteFetcherClient:
    return WebsiteFetcherClient(
        host="collector-server", port="55555"
    )  # TODO: move to settings
