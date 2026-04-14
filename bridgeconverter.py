import argparse

from bridge.drivers.input import InputDriver, get_input_driver_for
from bridge.drivers.output.pbn import PbnOutputDriver
from bridge.converters.lin_pbn import LinPbnConverter
from bridge.util.date import normalize_date


def parse_args():
    p = argparse.ArgumentParser()

    p.add_argument("--input-driver", default="stdin")
    p.add_argument("--input-format", default="lin")

    p.add_argument("--event")
    p.add_argument("--date")
    p.add_argument("--site", default="BBO")

    p.add_argument("--bfh-event-id", type=int)
    p.add_argument("--bfh-boards", default="all")

    p.add_argument("--bbo-url")

    return p.parse_args()


def main():
    args = parse_args()

    date = normalize_date(args.date) if args.date else None

    input_driver: InputDriver = get_input_driver_for(args)

    converter = LinPbnConverter(args.event, date, args.site)
    output_driver = PbnOutputDriver()

    records = []

    for entry in input_driver.load():
        try:
            records.append(converter.convert(entry.lin, extra={
                "contract": entry.contract,
                "declarer": entry.declarer,
                "result": entry.result,
                "lead": entry.lead,
                "score": entry.score,
            }))
        except Exception as e:
            records.append(f"{{ ERROR: {e} }}")

    output_driver.write(records)


if __name__ == "__main__":
    main()
