import sys
from argparse import Namespace
from typing import Iterator, Protocol, runtime_checkable

from bridge.drivers.input.bbo_url import BboUrlDriver
from bridge.drivers.input.bfh import BfhDriver
from bridge.drivers.input.stdin import StdinDriver
from bridge.model.entry import DealEntry


@runtime_checkable
class InputDriver(Protocol):
    def load(self) -> Iterator[DealEntry]:
        ...


def get_input_driver_for(args: Namespace) -> InputDriver:
    if args.input_driver == "stdin":
        return StdinDriver(args.input_format)

    if args.input_driver == "bfh":
        if not args.bfh_event_id:
            print("ERROR: --bfh-event-id required", file=sys.stderr)
            sys.exit(1)

        return BfhDriver(args.bfh_event_id, args.bfh_boards)

    if args.input_driver == "bbo-url":
        if not args.bbo_url:
            print("ERROR: --bbo-url required for bbo-url driver", file=sys.stderr)
            sys.exit(1)

        return BboUrlDriver(args.bbo_url)

    raise ValueError(f"Unknown input driver: {args.input_driver}")
