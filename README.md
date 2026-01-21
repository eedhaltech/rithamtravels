# Ritham Tours & Travels - Django Project

A complete, production-ready Django web application for a travel and tour booking company.

## Features

- 🔐 JWT Authentication (Customer & Travels/Admin separate logins)
- 🚗 Vehicle Booking System
- 📍 Multi-city Tour Planner
- 💳 Razorpay Payment Integration
- 📧 Email & WhatsApp Notifications
- 🌐 Bootstrap 5 Frontend
- 📱 Mobile Responsive Design
- 📝 Blog Management
- ⭐ Testimonials & Reviews
- 📊 Admin Dashboard

## Technology Stack

- **Backend**: Django 4.2, Django REST Framework
- **Authentication**: SimpleJWT
- **Database**: PostgreSQL/MySQL
- **Frontend**: Bootstrap 5, jQuery
- **Payment**: Razorpay
- **Deployment**: Gunicorn, WhiteNoise

## Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd ritham-tours
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables**
```bash
cp .env.example .env
# Edit .env with your settings
```

5. **Setup database**
```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py load_initial_data  # Load test data
```

6. **Run development server**
```bash
python manage.py runserver
```

Visit `http://127.0.0.1:8000/` in your browser.

## Environment Variables

Create a `.env` file in the project root with the following variables:

```
SECRET_KEY=your-secret-key-here
DEBUG=True
DB_NAME=ritham_tours
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432
RAZORPAY_KEY_ID=your-razorpay-key-id
RAZORPAY_KEY_SECRET=your-razorpay-key-secret
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-email-password
DEFAULT_FROM_EMAIL=noreply@rithamtours.com
WHATSAPP_API_KEY=your-whatsapp-api-key
WHATSAPP_API_SECRET=your-whatsapp-api-secret
```

## Project Structure

```
ritham-tours/
├── accounts/          # User authentication & profiles
├── bookings/          # Booking management & payments
├── vehicles/          # Vehicle management
├── tours/             # Tour packages & planning
├── blog/              # Blog posts
├── enquiries/         # Enquiries, testimonials, promotions
├── templates/         # HTML templates
├── static/            # Static files (CSS, JS, images)
├── media/             # User uploaded files
└── ritham_tours/      # Main project settings
```

## Key URLs

- Home: `/`
- Tour Planner: `/tour-planner/`
- Booking Status: `/booking-status/`
- Contact Us: `/contact-us/`
- Blog: `/blog/`
- Customer Login: `/customer-login/`
- Travels Login: `/travels-login/`
- Admin Panel: `/admin/`

## API Endpoints

- `POST /api/auth/customer/signup/` - Customer registration
- `POST /api/auth/travels/signup/` - Travels registration
- `POST /api/auth/customer/login/` - Customer login
- `POST /api/auth/travels/login/` - Travels login
- `POST /api/bookings/` - Create booking
- `GET /api/bookings/status/<booking_number>/` - Get booking status
- `POST /api/razorpay/order/` - Create Razorpay order
- `POST /api/razorpay/callback/` - Razorpay callback

## Test Data

The project includes a management command to load initial test data:

```bash
python manage.py load_initial_data
```

This will create:
- Sample vehicles
- Cities and routes
- Tour packages
- Sample blog posts

## Production Deployment

1. Set `DEBUG=False` in `.env`
2. Configure proper database credentials
3. Set up static files serving with WhiteNoise
4. Configure email settings
5. Set up Razorpay keys
6. Run migrations: `python manage.py migrate`
7. Collect static files: `python manage.py collectstatic`
8. Use Gunicorn: `gunicorn ritham_tours.wsgi:application`

## License

Copyright © 2024 Ritham Tours & Travels. All rights reserved.

