# 🛒 Online Store Website (Django E-Commerce)

A full-featured **E-Commerce Web Application** built with **Django**, supporting cart management, online payments, order tracking, PDF invoices, and modern UI.

This project demonstrates real-world backend development with authentication, payment integration, and API usage.

---

## 🚀 Live Features

- 🏠 Product listing with search & category filter
- 🛒 Add to Cart / Remove / Increase / Decrease quantity
- 💳 Secure Checkout with **Razorpay Integration**
- 📦 Order placement & tracking system
- 🧾 Downloadable **PDF Invoice**
- 👤 User Authentication (Login / Signup / Logout)
- 🖼 Profile management with image upload
- 📍 Auto-detect user location for address
- 📊 Admin Dashboard (manage users, products, orders)
- 🌐 Fetch products from external API
- 🎨 Clean and responsive UI (Amazon-style layout)

---

## 🛠 Tech Stack

| Technology        | Usage                  |
| ----------------- | ---------------------- |
| **Django**        | Backend Framework      |
| **Python**        | Core Programming       |
| **SQLite**        | Database               |
| **HTML/CSS/JS**   | Frontend               |
| **Razorpay**      | Payment Gateway        |
| **ReportLab**     | PDF Invoice Generation |
| **FakeStore API** | Product Data           |

---

## 📂 Project Structure

```
store_project/
│
├── store/                   # Main Django App
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   ├── templates/
│   ├── static/
│
├── store_project/           # Project Settings
│   ├── settings.py
│   ├── urls.py
│
├── media/                   # Uploaded images
├── static/                  # Static files (CSS/JS)
├── db.sqlite3               # Database
├── manage.py
├── requirements.txt
```

---

## ⚙️ Installation & Setup

### 1️⃣ Clone Repository

```bash
git clone https://github.com/your-username/online-store-website.git
cd store_project
```

---

### 2️⃣ Create Virtual Environment

```bash
python -m venv venv
venv\Scripts\activate   # Windows
```

---

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

---

### 4️⃣ Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

---

### 5️⃣ Create Superuser

```bash
python manage.py createsuperuser
```

---

### 6️⃣ Run Server

```bash
python manage.py runserver
```

👉 Open in browser:

```
http://127.0.0.1:8000/
```

---

## 💳 Razorpay Setup

Add your Razorpay keys in `settings.py`:

```python
RAZORPAY_KEY_ID = "your_key_id"
RAZORPAY_KEY_SECRET = "your_secret_key"
```

---

## 📍 Location Feature

Uses browser geolocation + OpenStreetMap API to auto-fill address during checkout.

---

## 🧾 PDF Invoice

Invoices are generated dynamically using **ReportLab** and downloaded as PDF files.

---

## 🌐 Fetch Products (API)

To load demo products:

```
http://127.0.0.1:8000/fetch-products/
```

---

## 📊 Admin Panel

Access admin dashboard:

```
http://127.0.0.1:8000/admin/
```

---

## 🚀 Deployment (Render)

1. Push code to GitHub
2. Go to Render
3. Create Web Service
4. Add:

```bash
gunicorn store_project.wsgi
```

5. Update settings:

```python
ALLOWED_HOSTS = ['*']
```

---

## 📸 Screenshots (Optional)

_Add your project screenshots here_

---

## 🔥 Future Improvements

- ⭐ Product Reviews & Ratings
- ❤️ Wishlist Feature
- 📧 Email Invoice System
- 🔐 OTP Login
- 📱 Fully responsive mobile UI

---

## 👨‍💻 Author

**Pabitra Swain**

- GitHub: https://github.com/PABITRASWAIN619
- Project: Online Store Website

---

## 📄 License

This project is for educational purposes and personal portfolio use.

---

## ⭐ Support

If you like this project, give it a ⭐ on GitHub!

---
