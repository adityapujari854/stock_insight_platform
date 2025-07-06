# 📈 Stock Insight Platform

A full-stack machine learning web application for predicting next-day stock prices using LSTM models. Built with Django, DRF, and Tailwind CSS, this platform integrates real-time prediction, Telegram bot support, user quota limits, JWT authentication, and Stripe payments.

---

## 🚀 Features

* ✅ User registration, login, and JWT-based authentication
* ✅ Predict next-day stock price using trained LSTM model
* ✅ Quota limits: 5 predictions/day for free users, unlimited for Pro
* ✅ Stripe integration for upgrading to Pro membership
* ✅ Telegram bot integration with `/start`, `/predict`, `/latest`
* ✅ AJAX-powered dashboard with dynamic result updates
* ✅ Admin dashboard for user and prediction management
* ✅ Dockerized deployment with production-ready settings

---

## 📂 Directory Structure

```
stock_insight_platform/
├── backend/
│   ├── billing/                # Stripe payment and webhook logic
│   ├── core/                   # Health check and base settings
│   ├── predictions/            # ML prediction logic and views
│   ├── users/                  # Auth, user models, TelegramUser
│   ├── templates/              # Frontend HTML (login, register, dashboard)
│   ├── staticfiles/            # Collected static files for Docker
│   ├── media/                  # Prediction plots storage
│   ├── manage.py               # Django CLI entry
│   ├── requirements.txt        # Python dependencies
│   └── Dockerfile              # API Dockerfile
├── docker-compose.yml          # Docker Compose for API container
└── README.md                   # Project documentation
```

---

## 🛠️ Tech Stack

* **Backend:** Django, Django REST Framework
* **Frontend:** Tailwind CSS, HTML templates
* **ML Model:** TensorFlow (LSTM-based `.keras` model)
* **Auth:** JWT (djangorestframework-simplejwt)
* **Payments:** Stripe API (test mode)
* **Telegram Bot:** python-telegram-bot v20
* **Containerization:** Docker + Gunicorn
* **Database:** SQLite (for development)

---

## ⚙️ Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/stock_insight_platform.git
cd stock_insight_platform
```

### 2. Create and configure `.env`

Create a file `backend/.env` with the following variables:

```env
DEBUG=True
SECRET_KEY=your_secret_key
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
CSRF_TRUSTED_ORIGINS=http://localhost

DATABASE_URL=sqlite:///db.sqlite3

EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend

JWT_ACCESS_LIFETIME=15
JWT_REFRESH_LIFETIME=1440

MODEL_PATH=model/stock_prediction_model.keras

STRIPE_PUBLIC_KEY=your_stripe_test_pk
STRIPE_SECRET_KEY=your_stripe_test_sk
STRIPE_WEBHOOK_SECRET=your_webhook_secret

BOT_TOKEN=your_telegram_bot_token

TAILWIND_APP_NAME=theme

STATIC_URL=/static/
MEDIA_URL=/media/

DJANGO_SETTINGS_MODULE=stock_insight.settings
PYTHONUNBUFFERED=1
```

### 3. Install dependencies (local)

```bash
cd backend
python -m venv venv
venv\Scripts\activate  # On Windows
pip install -r requirements.txt
```

### 4. Apply migrations

```bash
python manage.py migrate
```

### 5. Collect static files

```bash
python manage.py collectstatic
```

### 6. Run development server

```bash
python manage.py runserver
```

---

## 🧪 Prediction CLI & Telegram Bot

### Run CLI Prediction (e.g., for TSLA)

```bash
python manage.py predict --ticker TSLA
```

### Run Telegram Bot

```bash
python manage.py telegrambot
```

---

## 🐳 Docker Deployment

### Build and start services

```bash
docker compose up --build
```

* Visit the API: [http://localhost:8000](http://localhost:8000)
* Admin Panel: [http://localhost:8000/admin/](http://localhost:8000/admin/)
* Health Check: [http://localhost:8000/healthz/](http://localhost:8000/healthz/)

---

## 🔐 JWT Authentication

### Register a user

```http
POST /api/v1/register/
Content-Type: application/json

{
  "username": "john",
  "password": "securepass123"
}
```

### Obtain Token

```http
POST /api/v1/token/
Content-Type: application/json

{
  "username": "john",
  "password": "securepass123"
}
```

Use the `access` token in headers:

```
Authorization: Bearer <access_token>
```

---

## 📡 API Endpoints

| Endpoint               | Method | Description                   |
| ---------------------- | ------ | ----------------------------- |
| `/api/v1/register/`    | POST   | Register a new user           |
| `/api/v1/token/`       | POST   | Obtain JWT tokens             |
| `/api/v1/predict/`     | POST   | Predict next-day price        |
| `/api/v1/predictions/` | GET    | Get past predictions          |
| `/subscribe/`          | GET    | Stripe checkout session (Pro) |
| `/webhooks/stripe/`    | POST   | Stripe webhook endpoint       |
| `/healthz/`            | GET    | Health check endpoint         |

---

## 📊 Prediction Output Format

```json
{
  "ticker": "TSLA",
  "predicted_price": 313.97,
  "metrics": {
    "mse": 141.42,
    "rmse": 11.89,
    "r2": 0.96
  },
  "plot_1_url": "/media/predictions/tsla_plot1.png",
  "plot_2_url": "/media/predictions/tsla_plot2.png"
}
```
