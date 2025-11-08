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

Deployment and phone access
---------------------------

1) Quick local phone access with ngrok (fast, temporary)

```bash
# start the app in your virtualenv
python app.py

# in another terminal, install ngrok and run (example):
ngrok http 5000

# ngrok will print a public URL (https://xxxx.ngrok.io) — open that on your phone
```

2) Simple cloud deploy (Render / Railway / any Git-based host)

- Push this repo to GitHub.
- Create a new Web Service on Render (or similar). For Render:
  - Connect your GitHub repo
  - Build command: `pip install -r requirements.txt`
  - Start command (Procfile supported) uses `gunicorn app:app` (already in `Procfile`).
  - Set environment PORT if required (Render provides $PORT automatically).

Render and Railway will provide a public URL you can open on your phone. This
is recommended if you want persistent public access without running your
machine.

Notes on security and production readiness
- Use a proper SECRET_KEY, enable HTTPS by default (platforms like Render
  handle TLS), and move JSON storage to a database.

