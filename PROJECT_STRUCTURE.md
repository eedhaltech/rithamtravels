# Ritham Tours & Travels - Project Structure

```
ritham_tours/
├── manage.py                           # Django management script
├── .env.example                        # Environment variables template
├── .gitignore                          # Git ignore rules
├── README.md                           # Project documentation
├── requirements.txt                    # Python dependencies
├── SETUP.md                           # Setup instructions
│
├── ritham_tours/                      # Main Django project
│   ├── __init__.py
│   ├── admin.py                       # Admin customizations
│   ├── asgi.py                        # ASGI configuration
│   ├── patches.py                     # Custom patches
│   ├── settings.py                    # Django settings
│   ├── urls.py                        # Main URL configuration
│   └── wsgi.py                        # WSGI configuration
│
├── accounts/                          # User authentication & management
│   ├── __init__.py
│   ├── admin.py                       # User admin interface
│   ├── apps.py
│   ├── middleware.py                  # Custom middleware
│   ├── models.py                      # User models
│   ├── serializers.py                 # API serializers
│   ├── urls.py                        # Account URLs
│   ├── views.py                       # Account views
│   └── migrations/                    # Database migrations
│
├── tours/                             # Core tour management
│   ├── __init__.py
│   ├── admin.py                       # Tour admin interface
│   ├── apps.py
│   ├── models.py                      # Tour, City, Package models
│   ├── urls.py                        # Tour URLs
│   ├── views.py                       # Tour views & APIs
│   ├── migrations/                    # Database migrations
│   └── management/
│       └── commands/
│           └── create_tariff_data.py  # Tariff data creation
│
├── vehicles/                          # Vehicle management
│   ├── __init__.py
│   ├── admin.py                       # Vehicle admin
│   ├── apps.py
│   ├── models.py                      # Vehicle & tariff models
│   ├── serializers.py                 # Vehicle serializers
│   ├── urls.py                        # Vehicle URLs
│   ├── views.py                       # Vehicle views
│   └── migrations/                    # Database migrations
│
├── bookings/                          # Booking system
│   ├── __init__.py
│   ├── admin.py                       # Booking admin
│   ├── apps.py
│   ├── models.py                      # Booking & payment models
│   ├── signals.py                     # Booking signals
│   ├── urls.py                        # Booking URLs
│   ├── utils.py                       # Booking utilities
│   ├── views.py                       # Booking views & APIs
│   ├── migrations/                    # Database migrations
│   ├── management/
│   │   └── commands/
│   │       └── test_notifications.py  # Notification testing
│   └── services/
│       ├── email_service.py           # Email notifications
│       └── notification_service.py    # General notifications
│
├── enquiries/                         # Contact & enquiries
│   ├── __init__.py
│   ├── admin.py                       # Enquiry admin
│   ├── apps.py
│   ├── models.py                      # Enquiry & testimonial models
│   ├── urls.py                        # Enquiry URLs
│   ├── views.py                       # Enquiry views
│   ├── migrations/                    # Database migrations
│   └── management/                    # Management commands
│
├── blog/                              # Blog system
│   ├── __init__.py
│   ├── admin.py                       # Blog admin
│   ├── apps.py
│   ├── models.py                      # Blog post models
│   ├── urls.py                        # Blog URLs
│   ├── views.py                       # Blog views
│   ├── migrations/                    # Database migrations
│   └── management/                    # Management commands
│
├── seo/                               # SEO optimization
│   ├── __init__.py
│   ├── admin.py                       # SEO admin
│   ├── apps.py
│   ├── context_processors.py          # SEO context
│   ├── mixins.py                      # SEO mixins
│   ├── models.py                      # SEO models
│   ├── tests.py                       # SEO tests
│   ├── views.py                       # SEO views
│   ├── migrations/                    # Database migrations
│   ├── management/
│   │   └── commands/
│   │       ├── extract_head.py        # Head extraction
│   │       ├── seo_proof.py           # SEO validation
│   │       └── validate_seo.py        # SEO validation
│   └── templatetags/
│       └── seo_tags.py                # SEO template tags
│
├── templates/                         # HTML templates
│   ├── base.html                      # Base template with global modals
│   ├── about_us.html                  # About page
│   ├── accounts/                      # Account templates
│   │   ├── dashboard.html
│   │   ├── login.html
│   │   ├── profile.html
│   │   └── register.html
│   ├── admin/                         # Admin templates
│   ├── blog/                          # Blog templates
│   │   ├── blog_detail.html
│   │   └── blog_list.html
│   ├── bookings/                      # Booking templates
│   │   ├── booking.html
│   │   ├── booking_confirmation.html
│   │   ├── booking_details.html
│   │   ├── booking_not_found.html
│   │   ├── cancellation.html          # With modal system
│   │   ├── online_cab_booking.html    # Enhanced form validation
│   │   └── payment_success.html
│   ├── enquiries/                     # Enquiry templates
│   │   ├── contact_us.html
│   │   └── testimonials.html
│   ├── includes/                      # Reusable components
│   │   └── popup_modal.html
│   ├── seo/                           # SEO templates
│   │   ├── og_tags.html
│   │   ├── schema_org.html
│   │   ├── seo_meta.html
│   │   └── twitter_tags.html
│   ├── tours/                         # Tour templates
│   │   ├── home.html                  # Main homepage
│   │   ├── tariff_local_hour.html     # Dynamic tariff data
│   │   ├── tariff_outstation_day.html # Dynamic tariff data
│   │   ├── tariff_outstation_km.html  # Dynamic tariff data
│   │   └── tour_planner.html
│   └── travels/                       # Travel management
│       ├── cities_list.html
│       ├── local_areas_list.html
│       ├── package_form.html
│       ├── packages_list.html
│       ├── tour_planner.html
│       └── vehicles_list.html
│
├── static/                            # Static files
│   ├── css/
│   │   ├── custom.css                 # Main stylesheet
│   │   └── multicity-forms.css        # Multicity form styles
│   ├── js/
│   │   ├── main.js                    # Main JavaScript
│   │   ├── multicity-core-validation.js # Form validation
│   │   ├── multicity-sightseeing.js   # Sightseeing features
│   │   └── popup-system.js            # Modal system
│   ├── admin/                         # Django admin static files
│   ├── bolgs_images/                  # Blog images
│   └── tour/                          # Tour images
│
├── staticfiles/                       # Collected static files (production)
│   ├── admin/
│   ├── css/
│   ├── js/
│   └── rest_framework/
│
├── media/                             # User uploaded files
│   └── (empty - for uploads)
│
├── logs/                              # Application logs
│   ├── .gitkeep                       # Keep directory in git
│   ├── django.log                     # Django logs
│   ├── email.log                      # Email service logs
│   └── whatsapp.log                   # WhatsApp service logs
│
├── .kiro/                             # Kiro IDE configuration
│   └── specs/                         # Development specifications
│       ├── multicity-form-validation/
│       │   ├── design.md
│       │   ├── requirements.md
│       │   └── tasks.md
│       └── website-seo-optimization/
│           ├── design.md
│           ├── requirements.md
│           └── tasks.md
│
└── .vscode/                           # VS Code configuration
    └── settings.json
```

## 🏗️ **Architecture Overview:**

### **Core Django Apps:**
- **`tours/`** - Main business logic (tours, cities, packages, tariffs)
- **`vehicles/`** - Vehicle management and pricing
- **`bookings/`** - Booking system with payment integration
- **`accounts/`** - User authentication and management
- **`enquiries/`** - Contact forms and testimonials
- **`blog/`** - Content management system
- **`seo/`** - SEO optimization and meta management

### **Key Features:**
- **🎯 Dynamic Tariff System** - Database-driven pricing for all vehicle types
- **📱 Global Modal System** - Consistent Bootstrap modals replacing native alerts
- **✅ Enhanced Form Validation** - Multi-step forms with real-time validation
- **🔍 SEO Optimization** - Comprehensive SEO management system
- **💳 Payment Integration** - Razorpay payment gateway
- **📧 Notification System** - Email and WhatsApp notifications
- **📊 Admin Dashboard** - Complete backend management

### **Frontend Assets:**
- **Responsive Design** - Bootstrap 5 with custom styling
- **Interactive Forms** - Multi-city validation and booking flows
- **Modern UI** - Professional modals and user feedback
- **Mobile Optimized** - Works seamlessly on all devices

### **Database Models:**
- Users, Bookings, Payments, Vehicles, Tours, Cities, Testimonials, SEO data

This is a **production-ready Django application** for a tour and travel business with comprehensive booking, payment, and management capabilities.