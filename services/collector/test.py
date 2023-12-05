from common.grpc.clients import *

x = WebsiteFetcherClient("collector-server", 55555)
d = x.fetch_page("https://google.com")
print(d)
