# QR Product Transparency — Prototype

This is a small Flask prototype that lets a producer generate QR codes which
redirect consumers to a verified product information page. It demonstrates a
transparent label flow using ORS (Oral Rehydration Solution) as a demo.

Features:
- Producer form to pick or name a product and generate a QR
- QR links to `/product/<product_key>` with ingredients, composition, safety
- Color-coded safety indicators and icons for each chemical
- Feedback collection saved to `feedbacks.json` (local prototype storage)
- Link to official consumer helpline: https://consumerhelpline.gov.in/

Quick start (macOS / zsh):

1. Create a virtualenv and install dependencies

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Run the app

```bash
python app.py
```

3. Open http://127.0.0.1:5000/ in your browser to generate a QR.

Notes:
- `products.json` contains demo data for ORS. Replace or extend this file to add
  more verified products. In production, swap JSON for a proper database and
  add authentication and content verification flows.
- QR images are saved under `static/qrcodes/` and are served as static files.

Design intent and extension points (short):
- Modular routes make it easy to add `/admin` for producer verification.
- Feedback storage is intentionally simple; telemetry & moderation should be
  added before a public deployment.
