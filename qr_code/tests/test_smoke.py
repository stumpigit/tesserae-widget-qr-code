"""qr_code smoke tests for local, themeable QR payload rendering."""

from __future__ import annotations

import json
from pathlib import Path
from urllib.parse import quote

import pytest
from flask.testing import FlaskClient

PLUGIN_ROOT = Path(__file__).resolve().parents[1]


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
