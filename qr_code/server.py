"""Server-side QR payload builder for the qr_code widget."""

from __future__ import annotations

from typing import Any

import segno

_VALID_KINDS = {"text", "link", "wifi", "vcard"}
_VALID_WIFI_SECURITY = {"WPA", "WEP", "nopass"}


def _clean(value: Any) -> str:
    return str(value or "").strip()


def _wifi_escape(value: str) -> str:
    return "".join(f"\\{ch}" if ch in {'\\', ';', ',', ':', '"'} else ch for ch in value)


def _vcard_escape(value: str) -> str:
    return (
        value.replace("\\", "\\\\")
        .replace("\n", "\\n")
        .replace(";", "\\;")
        .replace(",", "\\,")
    )


def _normalise_url(value: str) -> str:
    url = _clean(value)
    if url and "://" not in url and not url.startswith(("mailto:", "tel:")):
        return f"https://{url}"
    return url


def _payload_for_text(options: dict[str, Any]) -> tuple[str, str]:
    text = _clean(options.get("text"))
    return text, text[:80]


def _payload_for_link(options: dict[str, Any]) -> tuple[str, str]:
    url = _normalise_url(options.get("url", ""))
    return url, url


def _payload_for_wifi(options: dict[str, Any]) -> tuple[str, str]:
    ssid = _clean(options.get("wifi_ssid"))
    if not ssid:
        return "", ""
    security = _clean(options.get("wifi_security")).upper() or "WPA"
    if security not in _VALID_WIFI_SECURITY:
        security = "WPA"
    password = "" if security == "nopass" else _clean(options.get("wifi_password"))
    hidden = "true" if options.get("wifi_hidden") is True else "false"
    payload = (
        f"WIFI:T:{security};S:{_wifi_escape(ssid)};"
        f"P:{_wifi_escape(password)};H:{hidden};;"
    )
    suffix = " (hidden)" if hidden == "true" else ""
    return payload, f"{ssid}{suffix}"


def _payload_for_vcard(options: dict[str, Any]) -> tuple[str, str]:
    name = _clean(options.get("vcard_name"))
    org = _clean(options.get("vcard_org"))
    phone = _clean(options.get("vcard_phone"))
    email = _clean(options.get("vcard_email"))
    url = _normalise_url(options.get("vcard_url", ""))
    if not any([name, org, phone, email, url]):
        return "", ""

    lines = ["BEGIN:VCARD", "VERSION:3.0"]
    if name:
        lines.append(f"FN:{_vcard_escape(name)}")
        lines.append(f"N:{_vcard_escape(name)};;;;")
    if org:
        lines.append(f"ORG:{_vcard_escape(org)}")
    if phone:
        lines.append(f"TEL;TYPE=CELL:{_vcard_escape(phone)}")
    if email:
        lines.append(f"EMAIL:{_vcard_escape(email)}")
    if url:
        lines.append(f"URL:{_vcard_escape(url)}")
    lines.append("END:VCARD")
    return "\n".join(lines), name or org or email or phone or url


def _build_payload(options: dict[str, Any]) -> tuple[str, str, str]:
    kind = _clean(options.get("kind")) or "link"
    if kind not in _VALID_KINDS:
        kind = "link"
    if kind == "text":
        payload, summary = _payload_for_text(options)
    elif kind == "wifi":
        payload, summary = _payload_for_wifi(options)
    elif kind == "vcard":
        payload, summary = _payload_for_vcard(options)
    else:
        payload, summary = _payload_for_link(options)
    return kind, payload, summary


def fetch(options: dict[str, Any], settings: dict[str, Any], ctx: dict[str, Any] | None = None) -> dict[str, Any]:
    del settings, ctx
    kind, payload, summary = _build_payload(options)
    title = _clean(options.get("title"))
    if not payload:
        return {"kind": kind, "title": title, "error": "Set QR code content in cell options."}

    qr = segno.make(payload, error="m", micro=False)
    matrix = ["".join("1" if cell else "0" for cell in row) for row in qr.matrix]
    return {
        "kind": kind,
        "title": title,
        "summary": summary,
        "matrix": matrix,
        "size": len(matrix),
        "quiet": 4,
    }
