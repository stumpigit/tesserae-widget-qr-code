"""qr_code smoke tests for local, themeable QR payload rendering."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from urllib.parse import quote

import pytest
from flask.testing import FlaskClient

PLUGIN_ROOT = Path(__file__).resolve().parents[1]


def _server_module():
    spec = importlib.util.spec_from_file_location("qr_code_server", PLUGIN_ROOT / "server.py")
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_qr_code_hides_details_by_default() -> None:
    manifest = json.loads((PLUGIN_ROOT / "plugin.json").read_text())
    show_details = next(option for option in manifest["cell_options"] if option["name"] == "show_details")

    assert show_details["default"] is False


def test_qr_code_details_do_not_show_technical_module_count() -> None:
    client_js = (PLUGIN_ROOT / "client.js").read_text()
    strings = {
        path.name: json.loads(path.read_text())
        for path in (PLUGIN_ROOT / "strings").glob("*.json")
    }

    assert "moduleLabel" not in client_js
    assert "modules" not in client_js
    assert all("modules" not in values for values in strings.values())


def test_wifi_password_is_secret_in_manifest() -> None:
    manifest = json.loads((PLUGIN_ROOT / "plugin.json").read_text())
    wifi_password = next(
        option for option in manifest["cell_options"] if option["name"] == "wifi_password"
    )

    assert wifi_password["secret"] is True


def test_fetch_does_not_return_raw_wifi_payload() -> None:
    server = _server_module()

    result = server.fetch(
        {
            "kind": "wifi",
            "wifi_ssid": "StudioNet",
            "wifi_password": "paper42",
            "wifi_security": "WPA",
        },
        {},
        None,
    )

    assert result["summary"] == "StudioNet"
    assert "payload" not in result
    assert "paper42" not in json.dumps(result)


def test_wifi_payload_escapes_double_quotes() -> None:
    server = _server_module()

    kind, payload, summary = server._build_payload(
        {
            "kind": "wifi",
            "wifi_ssid": 'Studio"Net',
            "wifi_password": 'paper"42',
            "wifi_security": "WPA",
        }
    )

    assert kind == "wifi"
    assert summary == 'Studio"Net'
    assert 'S:Studio\\"Net' in payload
    assert 'P:paper\\"42' in payload


@pytest.mark.parametrize(
    ("kind", "opts", "expected"),
    [
        ("text", {"kind": "text", "text": "Hello Tesserae"}, "Hello Tesserae"),
        ("link", {"kind": "link", "url": "https://docs.tesserae.ink"}, "https://docs.tesserae.ink"),
        (
            "wifi",
            {
                "kind": "wifi",
                "wifi_ssid": "StudioNet",
                "wifi_password": "paper42",
                "wifi_security": "WPA",
                "wifi_hidden": True,
            },
            "StudioNet",
        ),
        (
            "vcard",
            {
                "kind": "vcard",
                "vcard_name": "Ada Lovelace",
                "vcard_org": "Analytical Engines",
                "vcard_phone": "+44 20 1234 5678",
                "vcard_email": "ada@example.com",
                "vcard_url": "https://example.com/ada",
            },
            "Ada Lovelace",
        ),
    ],
)
def test_qr_code_renders_all_payload_kinds(client: FlaskClient, kind: str, opts: dict, expected: str) -> None:
    query_opts = quote(json.dumps(opts))
    resp = client.get(f"/_test/render?plugin=qr_code&size=md&opts={query_opts}")

    assert resp.status_code == 200
    body = resp.get_data(as_text=True)
    assert 'data-plugin="qr_code"' in body
    assert "data-data='null'" not in body
    assert f'"kind": "{kind}"' in body
    assert expected in body


@pytest.mark.parametrize("size", ["xs", "sm", "md", "lg"])
def test_qr_code_smoke_sizes(client: FlaskClient, size: str) -> None:
    opts = quote(json.dumps({"kind": "link", "url": "https://docs.tesserae.ink"}))
    resp = client.get(f"/_test/render?plugin=qr_code&size={size}&opts={opts}")

    assert resp.status_code == 200
    body = resp.get_data(as_text=True)
    assert 'data-plugin="qr_code"' in body
    assert "https://docs.tesserae.ink" in body
