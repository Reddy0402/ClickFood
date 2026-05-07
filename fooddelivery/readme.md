# ClickFood Premium 🍽️✨

A high-fidelity, state-of-the-art Django-based food delivery web application. **ClickFood Premium** pairs a luxurious dual-theme glassmorphic frontend with a robust, async-supported Django backend, featuring Groq AI culinary concierges and Stripe secure payment gateways.

---

## 🌟 Key Features

### 🔐 1. Glassmorphic User Portal
- **Combined Login & Signup**: Seamless form switching with smooth, high-fidelity slide transitions in a single layout.
- **Modern Interactions**: Floating text labels that animate on focus, password show/hide eye-toggles, and elegant dynamic validation alerts.
- **Auth Context integration**: Dynamically updates the global header to show personalized welcome greetings (`"Hi, <username>"`) and context-specific Sign In/Out buttons.

### 🛒 2. Asynchronous AJAX Cart Drawer
- **Page-Reload-Free Adding**: Instantly add, decrement, or update item quantities on the main menu using async `fetch` API endpoints.
- **Sliding Drawer**: Click the Cart button to slide open a beautiful cart drawer featuring in-memory item totals and backdrop blur overlays.

### 💳 3. Multi-Pathway Checkout Suite
- **Stripe Payments**: Real-time secure online credit card tokenization via Stripe Checkout Sessions (converting INR securely to Paise subunits).
- **Cash on Delivery (COD)**: Instantly processes orders using stored delivery address parameters.
- **Simulated Test Gateway**: Fast bank simulation gateway for instant end-to-end checkout testing.

### 📦 4. Live Order Progress Timeline
- **CSS-Animated Trackers**: Monitor active order statuses via a styled step-by-step progress timeline (`Placed` ➔ `Preparing` ➔ `On the Way` ➔ `Delivered`) with dynamic glowing status indicators.

### 🤖 5. Menu-Aware AI Culinary Concierge
- **Database Context Injection**: The chat widget parses active database `FoodItem` records in real time, compiling a personalized context prompt.
- **Groq Cloud Integration**: Processes recommendations using the hyper-fast `llama-3.1-8b-instant` model to suggest dishes, pairings, and combos in under 3 sentences.

### 🌗 6. Luxurious Dual HSL Theme System
- **Midnight Dark Mode**: Toggle between light and dark themes instantly. HSL-based styling variables ensure beautiful glassmorphic card reflections, smooth body background transitions, and visual consistency.

---

## 🛠️ Tech Stack

- **Backend Framework**: Django 4.x (Python)
- **Database**: SQLite (configured via Django ORM)
- **Frontend Core**: Vanilla HTML5, CSS3, ES6 JavaScript
- **Animations & Styling**: HSL Custom Tokens, VanillaTilt JS (3D Card Tilt), Boxicons, Google Fonts
- **Cloud Gateways**: Stripe Checkout API, Groq Cloud LLM API

---

## 🚀 Installation & Setup

### 1. Clone & Enter Project Directory
```bash
git clone https://github.com/Reddy0402/ClickFood.git
cd ClickFood/fooddelivery
```

### 2. Install Python Dependencies
```bash
pip install -r requirements.txt
```
*Note: Make sure `django`, `stripe`, `python-dotenv`, and `groq` are installed.*

### 3. Setup Secure Environment Variables (`.env`)
Create a `.env` file in the settings directory `fooddelivery/fooddelivery/.env` to secure your API keys:
```env
DJANGO_SECRET_KEY='your-django-secret-key'
DEBUG=True

# Groq AI Key
GROQ_API_KEY='gsk_...'

# Stripe Payments Key
STRIPE_SECRET_KEY='sk_test_...'
```
*(The local `.env` file is protected and ignored by `.gitignore` so your secret keys are never committed to GitHub).*

### 4. Database Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Run the Server
```bash
python manage.py runserver
```
Visit **[http://127.0.0.1:8000/](http://127.0.0.1:8000/)** in your browser and enjoy the premium experience!

---

## 📁 Project Structure

```
fooddelivery/
├── fooddelivery/         # Django settings, WSGI/ASGI configurations, and .env
├── orders/               # Primary App (models, views, URLs, templates)
│   ├── templates/        # HTML templates (home, cart, login, my_orders, address, etc.)
│   └── static/           # Global styles and client-side JavaScript controllers
├── db.sqlite3            # Local SQLite Database
├── manage.py             # Django admin controller
└── PROJECT_EXPLANATION.md # Universal master blueprint and internal execution guide
```

---

## 📄 License

This project is licensed under the MIT License.