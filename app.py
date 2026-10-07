from __future__ import annotations

import math
import random
from datetime import datetime
from functools import lru_cache
from io import BytesIO
from pathlib import Path

import qrcode
from flask import Flask, flash, jsonify, redirect, render_template, request, send_file, session, url_for

app = Flask(__name__)
app.secret_key = "manjrekar-masale-local-store"

WHATSAPP_NUMBER = "9136151859"
EMAIL = "smmitgm23@gmail.com"

PRODUCTS = [
    {"id": "amba-loncha", "name": "Amba Loncha", "category": "Loncha", "price": 200, "unit": "1 kg", "icon": "🥭", "description": "Fresh mango-based Loncha prepared with a balanced, fragrant spice blend.", "badge": "Offered price", "color": "#f4a623"},
    {"id": "limbu-loncha", "name": "Limbu Loncha", "category": "Loncha", "price": 200, "unit": "1 kg", "icon": "🍋", "description": "A bright lemon-inspired Loncha with a fresh, tangy finish.", "badge": "Offered price", "color": "#f2d85b"},
    {"id": "avla-loncha", "name": "Avla Loncha", "category": "Loncha", "price": 240, "unit": "1 kg", "icon": "🍏", "description": "A wholesome Amla-based Loncha with a rich, traditional flavour.", "badge": "Offered price", "color": "#9bcf69"},
    {"id": "mirchi-locha", "name": "Mirchi Locha", "category": "Loncha", "price": 200, "unit": "1 kg", "icon": "🌶️", "description": "A lively chilli-based Loncha made for a bold, savoury finish.", "badge": "Offered price", "color": "#d94b3d"},
    {"id": "mix-loncha", "name": "Mix Loncha", "category": "Loncha", "price": 200, "unit": "1 kg", "icon": "🥭", "description": "A mixed fruit and spice Loncha with a deliciously balanced taste.", "badge": "Offered price", "color": "#e28b53"},
    {"id": "amba-gavthi-loncha", "name": "Amba Gavthi Loncha", "category": "Loncha", "price": 240, "unit": "1 kg", "icon": "🥭", "description": "A rich Amba Gavthi-style Loncha prepared in the traditional way.", "badge": "Offered price", "color": "#e4a33f"},
    {"id": "amba-god-lomcha", "name": "Amba God Lomcha", "category": "Loncha", "price": 240, "unit": "1 kg", "icon": "🥭", "description": "A distinctive Amba God Lomcha with a deep, aromatic taste.", "badge": "Offered price", "color": "#d67d35"},
    {"id": "limbu-god-loncha", "name": "Limbu God Loncha", "category": "Loncha", "price": 240, "unit": "1 kg", "icon": "🍋", "description": "A tangy Lembu God Loncha with a traditional spice profile.", "badge": "Offered price", "color": "#f0cf50"},
    {"id": "avla-god-loncha", "name": "Avla God Loncha", "category": "Loncha", "price": 240, "unit": "1 kg", "icon": "🍏", "description": "A fruity Amla God Loncha with a wholesome, aromatic finish.", "badge": "Offered price", "color": "#75ad55"},
    {"id": "amba-muramba", "name": "Amba Muramba", "category": "Loncha", "price": 200, "unit": "1 kg", "icon": "🥭", "description": "A classic Amba Muramba Loncha with a warm, homemade flavour.", "badge": "Offered price", "color": "#c77731"},
    {"id": "malvani-masala", "name": "Malvani Masala", "category": "Masales", "price": 600, "unit": "1 kg", "icon": "🧂", "description": "Traditional Malvani masala with a rich, bold and deeply aromatic profile.", "badge": "Offered price", "color": "#9d4c36"},
    {"id": "special-malvani-masala", "name": "Special Malvani Masala", "category": "Masales", "price": 800, "unit": "1 kg", "icon": "🌶️", "description": "Our premium Special Malvani masala with an extra-rich spice blend.", "badge": "Offered price", "color": "#7c3429"},
    {"id": "ghati-masala", "name": "Ghati Masala", "category": "Masales", "price": 750, "unit": "1 kg", "icon": "🧂", "description": "A deeply aromatic Ghati masala made for bold, traditional meals.", "badge": "Offered price", "color": "#b6653d"},
]


def get_product(product_id: str):
    return next((p for p in PRODUCTS if p["id"] == product_id), None)


def price_for_size(base_price: int, size: str) -> int:
    if size == "250 g":
        return round(base_price / 4)
    if size == "500 g":
        return round(base_price / 2)
    return base_price


def get_cart():
    return session.get("cart", [])


def cart_count():
    return sum(item["quantity"] for item in get_cart())


def cart_total():
    total = 0
    for item in get_cart():
        total += (item.get("price", get_product(item["id"])["price"]) if get_product(item["id"]) else 0) * item["quantity"]
    return total


def whatsapp_message(order: dict) -> str:
    lines = [
        "Hello Manjrekar Masale! 👋",
        "I placed a new order.",
        "",
        "Order ID: " + order["order_id"],
        "Payment: " + order["payment_method"],
        "",
        "Customer details:",
        f"Name: {order['name']}",
        f"Phone: {order['phone']}",
        f"Email: {order['email']}",
        "",
        "Delivery address:",
        order["address"],
        "",
        "Items:",
    ]
    for item in order["items"]:
        lines.append(f"- {item['name']} ({item['size']}) × {item['quantity']} — ₹{item['price'] * item['quantity']}")
    lines.extend([
        "",
        f"Subtotal: ₹{order['subtotal']}",
        f"Delivery: ₹{order['delivery']}",
        f"Total: ₹{order['total']}",
        "",
        "Please confirm availability and delivery details.",
    ])
    return "\n".join(lines)


@app.get("/")
def home():
    featured = PRODUCTS[:4]
    return render_template("index.html", featured=featured, products=PRODUCTS[:4])


@app.get("/products")
def products_page():
    category = request.args.get("category", "all")
    products = PRODUCTS if category == "all" else [p for p in PRODUCTS if p["category"] == category]
    return render_template("products.html", products=products, category=category)


@app.get("/product/<product_id>")
def product_detail(product_id: str):
    product = get_product(product_id)
    if not product:
        return render_template("404.html"), 404
    return render_template("product.html", product=product, related=[p for p in PRODUCTS if p["category"] == product["category"] and p["id"] != product_id][:3])


@app.post("/cart/add")
def add_to_cart():
    product_id = request.form.get("product_id", "").strip()
    size = request.form.get("size", "1 kg")
    quantity = max(1, min(20, int(request.form.get("quantity", 1) or 1)))
    product = get_product(product_id)
    if not product:
        flash("That product is no longer available.", "error")
        return redirect(url_for("products_page"))
    if size not in {"1 kg", "250 g", "500 g"}:
        flash("Please select a valid pack size.", "error")
        return redirect(url_for("product_detail", product_id=product_id))

    price = price_for_size(product["price"], size)
    cart = get_cart()
    existing = next((item for item in cart if item["id"] == product_id and item.get("size") == size), None)
    if existing:
        existing["quantity"] = min(20, existing["quantity"] + quantity)
    else:
        cart.append({"id": product_id, "size": size, "price": price, "quantity": quantity})
    session["cart"] = cart
    flash(f"{product['name']} ({size}) added to your cart.", "success")
    return redirect(url_for("cart_page"))


@app.get("/cart")
def cart_page():
    cart_items = []
    for item in get_cart():
        product = get_product(item["id"])
        if product:
            cart_items.append({**product, "size": item.get("size", "1 kg"), "price": item.get("price", product["price"]), "quantity": item["quantity"]})
    return render_template("cart.html", cart_items=cart_items, subtotal=cart_total(), count=cart_count())


@app.post("/cart/update")
def update_cart():
    product_id = request.form.get("product_id", "")
    size = request.form.get("size", "1 kg")
    quantity = int(request.form.get("quantity", 1))
    cart = get_cart()
    if quantity <= 0:
        cart = [item for item in cart if not (item["id"] == product_id and item.get("size", "1 kg") == size)]
    else:
        for item in cart:
            if item["id"] == product_id and item.get("size", "1 kg") == size:
                item["quantity"] = min(20, quantity)
                break
    session["cart"] = cart
    return redirect(url_for("cart_page"))


@app.get("/checkout")
def checkout_page():
    cart_items = []
    for item in get_cart():
        product = get_product(item["id"])
        if product:
            cart_items.append({**product, "size": item.get("size", "1 kg"), "price": item.get("price", product["price"]), "size": item.get("size", "1 kg"), "price": item.get("price", product["price"]), "quantity": item["quantity"]})
    subtotal = cart_total()
    delivery = 49 if subtotal < 999 else 0
    if not cart_items:
        flash("Your cart is empty. Add a product before checking out.", "error")
        return redirect(url_for("products_page"))
    return render_template("checkout.html", cart_items=cart_items, subtotal=subtotal, delivery=delivery, total=subtotal + delivery)


@app.post("/checkout")
def checkout():
    required = ["name", "phone", "email", "address", "payment_method"]
    values = {key: request.form.get(key, "").strip() for key in required}
    errors = []
    if len(values["name"]) < 2:
        errors.append("Please enter your full name.")
    if not values["phone"].isdigit() or len(values["phone"]) < 10:
        errors.append("Please enter a valid phone number.")
    if "@" not in values["email"] or "." not in values["email"].split("@")[-1]:
        errors.append("Please enter a valid email address.")
    if len(values["address"]) < 15:
        errors.append("Please enter a complete delivery address.")
    if values["payment_method"] not in {"Cash on delivery", "UPI", "Bank transfer"}:
        errors.append("Please select a payment method.")

    if errors:
        for error in errors:
            flash(error, "error")
        return redirect(url_for("checkout_page"))

    cart_items = []
    for item in get_cart():
        product = get_product(item["id"])
        if product:
            cart_items.append({"name": product["name"], "size": item.get("size", "1 kg"), "quantity": item["quantity"], "price": item.get("price", product["price"])})
    subtotal = cart_total()
    delivery = 49 if subtotal < 999 else 0
    order = {
        "order_id": f"MM-{datetime.now().strftime('%d%m%Y')}-{random.randint(100, 999)}",
        "name": values["name"],
        "phone": values["phone"],
        "email": values["email"],
        "address": values["address"],
        "payment_method": values["payment_method"],
        "items": cart_items,
        "subtotal": subtotal,
        "delivery": delivery,
        "total": subtotal + delivery,
        "created_at": datetime.now().strftime("%d %B %Y, %I:%M %p"),
    }
    message = whatsapp_message(order)
    whatsapp_url = f"https://wa.me/91{WHATSAPP_NUMBER}?text={__import__('urllib.parse').parse.quote_plus(message)}"
    session.pop("cart", None)
    session["last_order"] = {**order, "whatsapp_url": whatsapp_url}
    return redirect(url_for("order_confirmation"))


@app.get("/order-confirmation")
def order_confirmation():
    order = session.get("last_order")
    if not order:
        return redirect(url_for("products_page"))
    return render_template("confirmation.html", order=order)


@app.get("/qr-code")
def whatsapp_qr():
    order = session.get("last_order")
    whatsapp_url = order.get("whatsapp_url", f"https://wa.me/91{WHATSAPP_NUMBER}") if order else f"https://wa.me/91{WHATSAPP_NUMBER}"
    qr = qrcode.QRCode(box_size=10, border=4)
    qr.add_data(whatsapp_url)
    qr.make(fit=True)
    image = BytesIO()
    qr.make_image(fill_color="black", back_color="white").save(image, format="PNG")
    image.seek(0)
    return send_file(image, mimetype="image/png", as_attachment=False, download_name="manjrekar-masale-whatsapp.png")


@app.get("/about")
def about():
    return render_template("about.html")


@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        if "@" not in email or "." not in email.split("@")[-1]:
            flash("Please enter a valid email address.", "error")
        else:
            flash("Thank you! We will send fresh updates to your inbox.", "success")
        return redirect(url_for("contact"))
    return render_template("contact.html", phone=WHATSAPP_NUMBER, email=EMAIL)


@app.get("/api/cart")
def cart_api():
    return jsonify({"count": cart_count(), "total": cart_total(), "items": get_cart()})


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
