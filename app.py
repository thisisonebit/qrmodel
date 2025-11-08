"""Flask QR-based Product Transparency Prototype

This app provides a simple producer-facing QR generator and a consumer-facing
product information page. It's intentionally minimal and modular so it can be
extended to use a real database or external verification pipelines later.

Core routes:
  - /           : QR generator form (producer)
  - /generate   : QR image for a product
  - /product/<k>: Product info page for consumers

Data storage:
  - products.json : temporary store of product details (hardcoded ORS initially)
  - feedbacks.json: appended feedback entries (local, temporary)

Security / deployment notes:
  - Meta tags and minimal headers are added in templates for SEO and preview
  - No authentication is implemented (prototype only)

This module uses qrcode and Pillow to generate QR images saved under
static/qrcodes. The product pages visualize chemical safety with simple
green/yellow/red indicators.

Authors: Prototype by project
"""

import json
import os
import io
from datetime import datetime

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    send_file,
    flash,
    abort,
    jsonify,
)
import qrcode

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "products.json")
FEEDBACK_FILE = os.path.join(BASE_DIR, "feedbacks.json")
QRCODE_DIR = os.path.join(BASE_DIR, "static", "qrcodes")
os.makedirs(QRCODE_DIR, exist_ok=True)

app = Flask(__name__)
# Use env SECRET_KEY when available for production; fallback for local dev
app.secret_key = os.environ.get("SECRET_KEY", "dev-key-for-prototype")


def load_products():
    """Load product data from one or more JSON files.

    Behavior:
      - If multiple product JSON files exist (e.g. `products.json`,
        `products_extra.json`), all entries are merged. Later files override
        earlier ones on key collisions. This lets us ship a small canonical
        file and then add a larger dataset for searchability.

    Returns:
        dict: mapping product_key -> product_data

    Example product_data structure:
    {
      "key": "ors",
      "name": "Oral Rehydration Solution",
      "ingredients": [
         {"name":"Glucose","amount":"13.5 g/L","safety":"safe"},
         {"name":"Sodium chloride","amount":"2.6 g/L","safety":"safe"}
      ],
      "composition": "Detailed composition text",
      "preparation": "Mix X with Y",
      "side_effects": ["nausea", "bloating"],
      "safety_flags": ["safe_for_children"]
    }
    """
    # Support multiple product files: any file starting with "products" and
    # ending with .json in the app dir will be loaded and merged.
    products = {}
    for fname in os.listdir(BASE_DIR):
        if fname.startswith("products") and fname.endswith(".json"):
            path = os.path.join(BASE_DIR, fname)
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    # Merge: later files override earlier keys
                    products.update(data)
            except Exception:
                # If a file is broken, skip it to avoid crashing the app.
                print(f"Warning: could not load product file {path}")
    return products



@app.route("/search")
def search_products():
    """Search products by name or ingredient.

    Query params:
      - q: the search query (partial match on product name or ingredient names)

    Returns JSON list of matching product summaries: [{key, name, short_name}]
    """
    q = (request.args.get("q") or "").strip().lower()
    products = load_products()
    if not q:
        # Return a short listing for client-side browsing (limit 50)
        out = [
            {"key": k, "name": v.get("name"), "short_name": v.get("short_name")}
            for k, v in list(products.items())[:50]
        ]
        return jsonify(out)

    matches = []
    for k, v in products.items():
        if q in k.lower() or q in v.get("name", "").lower():
            matches.append({"key": k, "name": v.get("name"), "short_name": v.get("short_name")})
            continue
        # search ingredients
        for ing in v.get("ingredients", []):
            if q in ing.get("name", "").lower():
                matches.append({"key": k, "name": v.get("name"), "short_name": v.get("short_name")})
                break
    # limit results
    return jsonify(matches[:50])


def save_feedback(entry: dict):
    """Append a feedback entry to the local feedbacks JSON file.

    Entry will include timestamp and product key. This is a simple local
    persistence mechanism to demonstrate collection; swap to a DB later.
    """
    existing = []
    if os.path.exists(FEEDBACK_FILE):
        try:
            with open(FEEDBACK_FILE, "r", encoding="utf-8") as f:
                existing = json.load(f)
        except Exception:
            existing = []
    existing.append(entry)
    with open(FEEDBACK_FILE, "w", encoding="utf-8") as f:
        json.dump(existing, f, indent=2)


def generate_qr(url: str, product_key: str) -> str:
    """Generate a QR code PNG for the given URL and save it to static/qrcodes.

    Returns the relative file path (from static) for embedding in templates.
    """
    filename = f"{product_key}.png"
    out_path = os.path.join(QRCODE_DIR, filename)
    qr = qrcode.QRCode(box_size=8, border=2)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    img.save(out_path)
    return f"qrcodes/{filename}"


@app.get("/healthz")
def healthz():
    """Simple health endpoint for deployment checks."""
    return {"status": "ok"}


@app.route("/", methods=["GET"])  # QR generator form
def index():
    products = load_products()
    # Provide a list of available product keys for quick selection
    return render_template("index.html", products=products)


@app.route("/generate", methods=["POST"])  # create and display QR
def generate():
    products = load_products()
    selected = request.form.get("product_select") or ""
    free_name = request.form.get("product_name", "").strip()
    # Normalize key: either pick selected or derive from free_name
    if selected:
        product_key = selected
    else:
        if not free_name:
            flash("Please provide a product name or select one.")
            return redirect(url_for("index"))
        product_key = free_name.lower().replace(" ", "-")

    # Build URL that the QR will encode
    product_url = url_for("product_page", product_key=product_key, _external=True)
    qr_rel_path = generate_qr(product_url, product_key)

    # If product not in products.json, show a notice but still generate QR for
    # a future onboarding flow (prototype behavior)
    product_info = products.get(product_key)
    return render_template(
        "generate.html",
        qr_path=url_for("static", filename=qr_rel_path),
        product_key=product_key,
        product_info=product_info,
        product_url=product_url,
    )


@app.route("/product/<product_key>", methods=["GET", "POST"])
def product_page(product_key):
    products = load_products()
    product = products.get(product_key)
    if request.method == "POST":
        # feedback submission
        name = request.form.get("name", "anonymous")
        comment = request.form.get("comment", "").strip()
        feedback_entry = {
            "product_key": product_key,
            "name": name,
            "comment": comment,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }
        save_feedback(feedback_entry)
        # also print to console for easy prototype visibility
        print("New feedback:", feedback_entry)
        flash("Thanks — your feedback has been recorded.")
        return redirect(url_for("product_page", product_key=product_key))

    if not product:
        # For unknown products we show a placeholder page that invites
        # producers to submit verified details in a future flow.
        return render_template("product.html", product=None, product_key=product_key)

    # Map safety levels to display classes and icons in template
    return render_template("product.html", product=product, product_key=product_key)


if __name__ == "__main__":
    # Run dev server. For production, use a WSGI server and set host/port there.
    app.run(debug=True, host="127.0.0.1", port=5000)
