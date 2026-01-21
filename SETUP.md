# Setup Instructions for Ritham Tours & Travels

## Quick Start Guide

### 1. Prerequisites
- Python 3.8 or higher
- PostgreSQL or MySQL database
- pip (Python package manager)

### 2. Installation Steps

#### Step 1: Clone and Navigate
```bash
cd "c:\ritham tours"
```

#### Step 2: Create Virtual Environment
```bash
python -m venv venv
venv\Scripts\activate  # On Windows
```

#### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

#### Step 4: Configure Environment
Create a `.env` file in the project root:
```
SECRET_KEY=your-secret-key-here
DEBUG=True
DB_NAME=ritham_tours
DB_USER=postgres
DB_PASSWORD=your-password
DB_HOST=localhost
DB_PORT=5432
RAZORPAY_KEY_ID=your-key-id
RAZORPAY_KEY_SECRET=your-key-secret
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-email-password
```

#### Step 5: Database Setup
```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py load_initial_data
```

#### Step 6: Run Server
```bash
python manage.py runserver
```

Visit: http://127.0.0.1:8000/

## Configuration Details

### Database Setup (PostgreSQL)
1. Install PostgreSQL
2. Create database: `CREATE DATABASE ritham_tours;`
3. Update `.env` with database credentials

### Database Setup (MySQL)
1. Install MySQL
2. Create database: `CREATE DATABASE ritham_tours;`
3. Uncomment MySQL configuration in `settings.py`
4. Update `.env` with database credentials

### Razorpay Setup
1. Sign up at https://razorpay.com
2. Get your Key ID and Key Secret from dashboard
3. Add to `.env` file

### Email Setup (Gmail)
1. Enable "Less secure app access" or use App Password
2. Add email credentials to `.env`

## Admin Access

After creating superuser, access admin at:
http://127.0.0.1:8000/admin/

## Default Test Data

The `load_initial_data` command creates:
- 8 vehicles (Swift Dzire, Etios, Innova, etc.)
- 11 cities (Coimbatore, Ooty, Kodaikanal, etc.)
- Routes between cities
- Tour packages
- Blog posts
- Testimonials
- Promotions

## Troubleshooting

### Database Connection Error
- Check database credentials in `.env`
- Ensure database server is running
- Verify database exists

### Static Files Not Loading
```bash
python manage.py collectstatic
```

### Migration Issues
```bash
python manage.py makemigrations
python manage.py migrate
```

### Import Errors
- Ensure virtual environment is activated
- Reinstall requirements: `pip install -r requirements.txt`

## Production Deployment

1. Set `DEBUG=False` in `.env`
2. Update `ALLOWED_HOSTS` in `settings.py`
3. Configure proper database
4. Set up static file serving
5. Use Gunicorn: `gunicorn ritham_tours.wsgi:application`
6. Configure web server (Nginx/Apache)

## Support

For issues or questions, please contact the development team.

