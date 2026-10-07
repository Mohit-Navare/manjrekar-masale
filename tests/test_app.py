import app as store


def test_home_and_products_render():
    client = store.app.test_client()
    home = client.get("/")
    products = client.get("/products")
    assert home.status_code == 200
    assert b"Manjrekar Masale" in home.data
    assert products.status_code == 200
    assert b"Amba Loncha" in products.data
    assert b"Special Malvani Masala" in products.data


def test_size_options_are_added_to_cart_and_whatsapp_order():
    client = store.app.test_client()
    detail = client.get("/product/amba-loncha")
    assert detail.status_code == 200
    assert b"250 g" in detail.data
    assert b"500 g" in detail.data

    response = client.post("/cart/add", data={"product_id": "amba-loncha", "size": "250 g", "quantity": 1})
    assert response.status_code == 302
    with client.session_transaction() as session:
        assert session["cart"][0]["size"] == "250 g"
        assert session["cart"][0]["price"] == 50


def test_cart_add_and_checkout_whatsapp_flow():
    client = store.app.test_client()
    with client.session_transaction() as session:
        session["cart"] = [{"id": "amba-loncha", "quantity": 2}]
    response = client.get("/checkout")
    assert response.status_code == 200
    assert b"Cash on delivery" in response.data

    response = client.post("/checkout", data={
        "name": "Asha Mehta",
        "phone": "9136151859",
        "email": "asha@example.com",
        "address": "12 Green Park, Pune, Maharashtra, 411001",
        "payment_method": "Cash on delivery",
    })
    assert response.status_code == 302
    response = client.get("/order-confirmation")
    assert response.status_code == 200
    assert b"Order received" in response.data
    assert b"wa.me/919136151859" in response.data


def test_whatsapp_qr_code_endpoint_returns_png():
    client = store.app.test_client()
    with client.session_transaction() as session:
        session["last_order"] = {"whatsapp_url": "https://wa.me/919136151859?text=Hello"}
    response = client.get("/qr-code")
    assert response.status_code == 200
    assert response.mimetype == "image/png"
    assert response.data.startswith(b"\x89PNG\r\n\x1a\n")


def test_invalid_checkout_is_rejected():
    client = store.app.test_client()
    with client.session_transaction() as session:
        session["cart"] = [{"id": "mirchi-locha", "quantity": 1}]
    response = client.post("/checkout", data={
        "name": "A",
        "phone": "123",
        "email": "bad",
        "address": "short",
        "payment_method": "Cash on delivery",
    })
    assert response.status_code == 302
    assert client.get("/checkout").status_code == 200
