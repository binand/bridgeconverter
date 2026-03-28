import json
import urllib.request

from bridge.model.entry import DealEntry


class BfhDriver:

    def __init__(self, event_id: int, boards: str):
        self.event_id = event_id
        self.boards_spec = boards

    # ---------------- Board parsing ---------------- #

    def _parse_boards(self):
        spec = self.boards_spec.strip()

        if spec == "all":
            # Default assumption (can be improved later)
            return list(range(1, 17))

        boards = set()

        parts = spec.split(",")

        for part in parts:
            part = part.strip()

            if not part:
                raise ValueError("Invalid boards spec: empty token")

            if "-" in part:
                try:
                    start, end = map(int, part.split("-", 1))
                except ValueError:
                    raise ValueError(f"Invalid range: '{part}'")

                if start > end:
                    raise ValueError(
                        f"Invalid range '{part}': start ({start}) must be <= end ({end})"
                    )

                boards.update(range(start, end + 1))

            else:
                try:
                    boards.add(int(part))
                except ValueError:
                    raise ValueError(f"Invalid board number: '{part}'")

        return sorted(boards)

    # ---------------- HTTP fetch ---------------- #

    def _fetch(self, board_no: int):
        url = (
            "https://bridgefromhome.com/wp-admin/admin-ajax.php"
            f"?action=bfh_result&mode=imp_pairs"
            f"&event_id={self.event_id}"
            f"&board_scoring_method=CROSS_IMPS"
            f"&q=board&board_number={board_no}"
        )


        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": "curl/8.15.0",
                "Accept": "*/*",
            }
        )

        with urllib.request.urlopen(req) as resp:
            return resp.read().decode("utf-8")

    # ---------------- Main entry ---------------- #

    def load(self):
        boards = self._parse_boards()

        for b in boards:
            try:
                text = self._fetch(b)
            except Exception as e:
                raise RuntimeError(f"Failed to fetch board {b}: {e}")

            try:
                data = json.loads(text)
            except Exception as e:
                raise RuntimeError(f"Invalid JSON for board {b}: {e}")

            if not data:
                # Not treating as fatal — just skip
                continue

            for e in data:
                lin = e.get("lin_data")

                if not lin:
                    continue

                yield DealEntry(
                    lin=lin,
                    contract=e.get("contract"),
                    declarer=e.get("played_by"),
                    result=e.get("tricks"),
                    lead=e.get("lead"),
                    score=e.get("score"),
                )
