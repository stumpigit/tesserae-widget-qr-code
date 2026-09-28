# Tesserae QR Code Widget

A theme-aware QR code widget for [Tesserae](https://github.com/dmellok/tesserae).
It generates QR codes for text, links, Wi-Fi credentials, and vCards.

## Features

- Text, link, Wi-Fi, and vCard QR payloads
- Server-side QR generation with `segno`
- No network access and no plugin settings required
- Uses Tesserae Spectra theme tokens for colour
- Minimal default display: QR code only
- Optional details view with title, type, content summary, and scan hint

## Tesserae catalog

This widget is intended to be installed through the Tesserae community catalog.
The plugin folder is `qr_code/`.

## Options

- `kind`: `text`, `link`, `wifi`, or `vcard`
- `show_details`: show title and human-readable details below the QR code
- `tone`: choose theme text colour or one of the theme accent slots
- Payload fields for the selected QR type

## Capabilities

`requires` is an empty list. The widget does not perform network requests, read
Tesserae settings, or write files outside the normal plugin runtime.

## Development

From a Tesserae checkout, copy this `qr_code/` folder into `plugins/qr_code/`,
then run:

```sh
uv run --extra dev python -m pytest plugins/qr_code/tests/test_smoke.py -q
uv run --extra dev ruff check plugins/qr_code
node --check plugins/qr_code/client.js
```

## License

AGPL-3.0-or-later.
