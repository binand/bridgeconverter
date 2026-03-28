import urllib.parse

from bridge.model.entry import DealEntry


class BboUrlDriver:

    def __init__(self, url: str):
        self.url = url

    def load(self):
        parsed = urllib.parse.urlparse(self.url)
        qs = urllib.parse.parse_qs(parsed.query)

        lin_list = qs.get("lin")

        if not lin_list or not lin_list[0]:
            raise ValueError("No 'lin' parameter found in BBO URL")

        lin = lin_list[0]

        # Do NOT unquote here — converter already does it
        yield DealEntry(lin=lin)
