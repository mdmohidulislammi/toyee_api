# Toyee – Baby Toy E‑commerce Platform

Toyee is a full‑stack e‑commerce web application for baby toys. It provides a smooth shopping experience with product browsing, filtering, cart, order placement, user profiles, and a powerful admin dashboard. The project uses **Django REST Framework** on the backend and **React** (with Tailwind CSS) on the frontend.

---

##  Features

### For customers
- Browse products by category, age, and price
- Search products with instant redirect
- View product details with image gallery
- Add to cart, update quantity, remove items
- Secure checkout with order placement
- User registration / login (JWT authentication)
- Order history with status tracking
- User profile (update name, address, phone)

### For admin (staff users)
- Dashboard with key metrics (users, products, orders, revenue)
- Full product management (add, edit, delete, toggle availability)
- Image upload for products
- User management (promote to admin, delete users)
- Order management (view all orders, update status to pending / processing / shipped / delivered)
- Category management (categories are created automatically via script)

### Additional
- Contact form that sends emails to admin (Gmail SMTP)
- Order confirmation email sent to customers
- Responsive design for mobile, tablet, and desktop

---

## 🛠️ Tech Stack

**Backend**
- Django 5.x / Django REST Framework
- PostgreSQL (or SQLite for development)
- Simple JWT (authentication)
- django‑cors‑headers
- django‑dotenv (environment variables)
- Gmail SMTP for emails

**Frontend**
- React 18
- React Router v6
- Axios
- Tailwind CSS
- Context API (state management)

**Tools**
- Git & GitHub
- VS Code
- Postman (API testing)

---

## 📦 Installation

### Prerequisites
- Python 3.10+ and pip
- Node.js 18+ and npm / yarn
- PostgreSQL (optional, SQLite works for development)

### 1. Clone the repository
```bash
git clone https://github.com/mdmohidulislammi/Learning/tree/main/React/E-commerce%20project
cd toyee