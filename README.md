# Bridge Deal Record Converter

A simple tool to convert bridge deal records from the Bridge Base Online (BBO)
specific LIN format to the more common Portable Bridge Notation (PBN).

---

## Features

- Convert LIN to PBN
- Supports:
  - Raw LIN
  - BBO Handviewer URLs
  - BridgeFromHome Ajax URLs
- Handles:
  - Partial hands (reconstructs 4th hand when possible)
  - Incomplete play / auction
- Adds metadata:
  - Event, Site, Date
  - Contract, Declarer, Result, Lead, Score

---

## Installation

Make the script executable:

chmod +x bridgeconverter

(Optional) Add to PATH:

mkdir -p ~/bin
mv bridgeconverter ~/bin/
export PATH="$HOME/bin:$PATH"

---

## Usage

### 1. From LIN (stdin)

cat input.lin | bridgeconverter > output.pbn

---

### 2. From BFH JSON (via curl)

curl -fsS "<bfh-url>" \
  | bridgeconverter \
      --input-driver=stdin \
      --input-format=bfh-json \
      --event="PUB Pairs" \
      --date="2026-03-01" \
  > output.pbn

---

### 3. Direct BFH fetch

bridgeconverter \
  --input-driver=bfh \
  --bfh-event-id=360 \
  --bfh-boards=1-16 \
  --event="PUB Pairs" \
  --date="2026-03-01" \
  > event.pbn

---

### 4. BBO Handviewer URL

bridgeconverter \
  --input-driver=bbo-url \
  --bbo-url=https://www.bridgebase.com/tools/handviewer.html?lin=... \
  --bfh-boards=1-16 \
  --event="PUB Pairs" \
  --date="2026-03-01" \
  > event.pbn

---

## Boards Specification

--bfh-boards supports:

- Single board: 5
- Multiple boards: 1,3,7
- Range: 1-16
- Combination: 1,3-5,8

Invalid ranges (e.g. 5-3) result in an error.

---

## Output

Generated PBN includes:

- Deal
- Auction
- Play (if available)
- Metadata tags:
  - Event, Site, Date
  - Contract, Declarer, Result, Lead, Score
- Diagnostics:
  - { INFO: ... }
  - { ERROR: ... }

---

## Dependencies

- Python 3.9+
- python-dateutil

Install:

pip install python-dateutil

---

## License

GPLv3 (https://www.gnu.org/licenses/gpl-3.0.en.html)
