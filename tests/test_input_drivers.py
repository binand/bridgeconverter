from argparse import Namespace
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import bridgeconverter
from bridge.drivers.input import InputDriver, get_input_driver_for
from bridge.model.entry import DealEntry


def make_args(**overrides):
    values = {
        "input_driver": "stdin",
        "input_format": "lin",
        "event": None,
        "date": None,
        "site": "BBO",
        "bfh_event_id": None,
        "bfh_boards": "all",
        "bbo_url": None,
    }
    values.update(overrides)
    return Namespace(**values)


def test_get_input_driver_for_stdin_returns_input_driver():
    driver = get_input_driver_for(make_args(input_driver="stdin", input_format="bfh-json"))

    assert isinstance(driver, InputDriver)
    assert driver.input_format == "bfh-json"


def test_get_input_driver_for_bfh_returns_input_driver():
    driver = get_input_driver_for(make_args(input_driver="bfh", bfh_event_id=123, bfh_boards="1-4"))

    assert isinstance(driver, InputDriver)
    assert driver.event_id == 123
    assert driver.boards_spec == "1-4"


def test_get_input_driver_for_bbo_url_returns_input_driver():
    url = "https://www.bridgebase.com/tools/handviewer.html?lin=test"
    driver = get_input_driver_for(make_args(input_driver="bbo-url", bbo_url=url))

    assert isinstance(driver, InputDriver)
    assert driver.url == url


def test_get_input_driver_for_bfh_requires_event_id(capsys):
    with pytest.raises(SystemExit) as exc_info:
        get_input_driver_for(make_args(input_driver="bfh"))

    captured = capsys.readouterr()

    assert exc_info.value.code == 1
    assert captured.err.strip() == "ERROR: --bfh-event-id required"


def test_get_input_driver_for_bbo_url_requires_url(capsys):
    with pytest.raises(SystemExit) as exc_info:
        get_input_driver_for(make_args(input_driver="bbo-url"))

    captured = capsys.readouterr()

    assert exc_info.value.code == 1
    assert captured.err.strip() == "ERROR: --bbo-url required for bbo-url driver"


def test_main_uses_opaque_input_driver(monkeypatch):
    class FakeInputDriver:
        def load(self):
            yield DealEntry(lin="lin-data")

    fake_args = make_args()
    observed = {}

    def fake_parse_args():
        return fake_args

    def fake_get_input_driver_for(args):
        observed["args"] = args
        return FakeInputDriver()

    class FakeConverter:
        def __init__(self, event, date, site):
            observed["converter_args"] = (event, date, site)

        def convert(self, lin, extra):
            observed["convert_call"] = (lin, extra)
            return "converted-record"

    class FakeOutputDriver:
        def write(self, records):
            observed["records"] = records

    monkeypatch.setattr(bridgeconverter, "parse_args", fake_parse_args)
    monkeypatch.setattr(bridgeconverter, "get_input_driver_for", fake_get_input_driver_for)
    monkeypatch.setattr(bridgeconverter, "LinPbnConverter", FakeConverter)
    monkeypatch.setattr(bridgeconverter, "PbnOutputDriver", FakeOutputDriver)

    bridgeconverter.main()

    assert observed["args"] is fake_args
    assert observed["converter_args"] == (None, None, "BBO")
    assert observed["convert_call"] == (
        "lin-data",
        {
            "contract": None,
            "declarer": None,
            "result": None,
            "lead": None,
            "score": None,
        },
    )
    assert observed["records"] == ["converted-record"]
