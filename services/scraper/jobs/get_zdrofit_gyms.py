import httpx


def get_zdrofit_gyms():
    print('called')
    r = httpx.post("http://crawler:6800/schedule.json", data={"project": "default", "spider": "zdrofit_gym"})
    print(r.status_code, r.text, 'AAA')
