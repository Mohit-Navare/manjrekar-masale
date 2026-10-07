# Manjrekar Masale Store

A complete Flask e-commerce website for handcrafted pickles and spice masalas.

## Features

- Responsive homepage and product catalog
- Pickle and masala product categories
- Product detail pages
- Cart add, remove, and quantity update
- Checkout with customer name, phone, email, address, and payment options
- Order total and delivery charge calculation
- WhatsApp order message containing customer details, payment, address, and items
- Mobile-friendly design

## Run locally

```powershell
cd "C:\Users\Mohit\Desktop\MM(smeet)"
python -m pip install -r requirements.txt
python app.py
```

Open [http://localhost:5000](http://localhost:5000) in your browser.

## Deploy to Render

1. Push the repository to GitHub, GitLab, or Bitbucket.
2. In Render, select **New → Blueprint**.
3. Connect the repository and choose the `render.yaml` configuration file.
4. Select **Create Blueprint** and wait for the service to deploy.
5. Open the generated URL to view the storefront.

The deployment uses Waitress 3.0.2 and serves the Flask application through the `app:app` entry point.

## Contact

- Phone: +91 9136151859
- Email: [smmitgm23@gmail.com](mailto:smmitgm23@gmail.com)

## Test

```powershell
python -m pytest -q
```
