# bridge/converters/lin_pbn.py

import urllib.parse

RANKS = "AKQJT98765432"
SUITS = "SHDC"

FULL_DECK = {s + r for s in SUITS for r in RANKS}


class LinPbnConverter:

    def __init__(self, event=None, date=None, site=None):
        self.event = event
        self.date = date
        self.site = site

    def convert(self, lin: str, extra=None) -> str:
        return lin_to_pbn(
            lin,
            context={
                "event": self.event,
                "date": self.date,
                "site": self.site,
            },
            extra=extra or {},
        )


# ---------------- Core parsing ---------------- #

def normalize_bid(b):
    b = b.strip()
    if b.lower() == "p":
        return "P"
    if b.lower() == "d":
        return "X"
    if b.lower() == "r":
        return "XX"
    return b.upper()


def parse_lin(lin_str):
    lin = urllib.parse.unquote(lin_str.strip())
    lin = lin.replace("\n", "")

    tokens = lin.split("|")

    pairs = []
    i = 0
    while i < len(tokens) - 1:
        pairs.append((tokens[i].strip(), tokens[i + 1].strip()))
        i += 2

    data = {
        "md": None,
        "sv": None,
        "mb": [],
        "pc": [],
        "pn": None,
        "ah": None,
    }

    for tag, val in pairs:
        if tag == "md":
            data["md"] = val
        elif tag == "sv":
            data["sv"] = val
        elif tag == "mb":
            data["mb"].append(normalize_bid(val))
        elif tag == "pc":
            data["pc"].append(val.upper())
        elif tag == "pn":
            data["pn"] = val.split(",")
        elif tag == "ah":
            data["ah"] = val

    if not data["md"]:
        raise ValueError("No md tag found")

    return data


def parse_hand(hand_str):
    cards = []
    suit = None
    for ch in hand_str:
        if ch in SUITS:
            suit = ch
        else:
            cards.append(suit + ch)
    return cards


def format_hand(cards):
    suits = {s: [] for s in SUITS}
    for c in cards:
        suits[c[0]].append(c[1])

    for s in SUITS:
        suits[s].sort(key=lambda x: RANKS.index(x))

    return ".".join("".join(suits[s]) for s in SUITS)


def reconstruct_hands(md):
    dealer = int(md[0])
    hands_raw = md[1:].split(",")

    hands = []
    used = set()

    for h in hands_raw:
        if h:
            cards = parse_hand(h)
            hands.append(cards)
            used.update(cards)
        else:
            hands.append([])

    diagnostics = []

    non_empty = [h for h in hands if h]
    total_cards = sum(len(h) for h in non_empty)

    if len(non_empty) == 3 and total_cards == 39:
        missing = list(FULL_DECK - used)
        for i in range(4):
            if not hands[i]:
                hands[i] = missing
                diagnostics.append(("INFO", f"Reconstructed missing hand at index {i}"))
                break
    else:
        diagnostics.append(
            ("INFO", f"No reconstruction (hands={len(non_empty)}, cards={total_cards})")
        )

    return dealer, hands, diagnostics


def validate_hands(hands):
    diagnostics = []

    all_cards = [c for h in hands for c in h]

    if len(all_cards) != len(set(all_cards)):
        diagnostics.append(("ERROR", "Duplicate cards detected"))

    sizes = [len(h) for h in hands if h]
    if sizes and (max(sizes) - min(sizes) > 1):
        diagnostics.append(("ERROR", f"Inconsistent hand sizes: {sizes}"))

    return diagnostics


def extract_players(pn):
    if not pn or len(pn) != 4:
        return None

    return {
        "South": pn[0].strip(),
        "West": pn[1].strip(),
        "North": pn[2].strip(),
        "East": pn[3].strip(),
    }


# ---------------- Conversion ---------------- #

def lin_to_pbn(lin_str, context=None, extra=None):
    if context is None:
        context = {}
    if extra is None:
        extra = {}

    data = parse_lin(lin_str)

    dealer_map = {1: "S", 2: "W", 3: "N", 4: "E"}
    vuln_map = {"n": "None", "o": "NS", "e": "EW", "b": "All"}

    dealer_num, hands, d1 = reconstruct_hands(data["md"])
    d2 = validate_hands(hands)
    diagnostics = d1 + d2

    dealer = dealer_map[dealer_num]

    order = [2, 3, 0, 1]
    deal = "N:" + " ".join(format_hand(hands[i]) for i in order)

    players = extract_players(data["pn"])

    auction = data["mb"]
    play = data["pc"]

    out = []

    # ---- Context metadata ----
    if context.get("event"):
        out.append(f'[Event "{context["event"]}"]')

    if context.get("site"):
        out.append(f'[Site "{context["site"]}"]')

    if context.get("date"):
        out.append(f'[Date "{context["date"]}"]')

    # ---- Players ----
    if players:
        for seat in ["North", "East", "South", "West"]:
            out.append(f'[{seat} "{players[seat]}"]')

    # ---- Board ----
    if data["ah"]:
        try:
            board_no = data["ah"].split()[-1]
            out.append(f'[Board "{board_no}"]')
        except Exception:
            pass

    out.append(f'[Dealer "{dealer}"]')
    out.append(f'[Vulnerable "{vuln_map.get(data["sv"], "None")}"]')
    out.append(f'[Deal "{deal}"]')

    # ---- Extra metadata ----
    if extra.get("contract"):
        out.append(f'[Contract "{extra["contract"]}"]')

    if extra.get("declarer"):
        out.append(f'[Declarer "{extra["declarer"]}"]')

    if extra.get("result"):
        out.append(f'[Result "{extra["result"]}"]')

    if extra.get("lead"):
        out.append(f'[Lead "{extra["lead"]}"]')

    if extra.get("score"):
        out.append(f'[Score "{extra["score"]}"]')

    # ---- Diagnostics ----
    for lvl, msg in diagnostics:
        out.append(f'{{ {lvl}: {msg} }}')

    # ---- Auction ----
    if auction:
        out.append(f'[Auction "{dealer}"]')
        out.extend(" ".join(auction[i:i + 4]) for i in range(0, len(auction), 4))

    # ---- Play ----
    if play:
        leader = extra.get("lead") or ""
        out.append(f'[Play "{leader}"]')
        out.extend(" ".join(play[i:i + 4]) for i in range(0, len(play), 4))

    return "\n".join(out)
