import sys
import json
from bridge.model.entry import DealEntry

class StdinDriver:

    def __init__(self, input_format: str):
        self.input_format = input_format

    def load(self):
        text = sys.stdin.read().strip()

        if self.input_format == "bfh-json":
            data = json.loads(text)

            for e in data:
                yield DealEntry(
                    lin=e.get("lin_data"),
                    contract=e.get("contract"),
                    declarer=e.get("played_by"),
                    result=e.get("tricks"),
                    lead=e.get("lead"),
                    score=e.get("score"),
                )
        else:
            for block in text.split("\n\n"):
                block = block.strip()
                if block:
                    yield DealEntry(lin=block)
