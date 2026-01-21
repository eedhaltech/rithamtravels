from django.urls import path
from . import views

urlpatterns = [
    path('contact-us/', views.ContactUsView.as_view(), name='contact_us'),
    path('testimonials/', views.TestimonialsView.as_view(), name='testimonials'),
    path('api/enquiries/', views.create_enquiry, name='create_enquiry'),
    path('api/testimonials/', views.create_testimonial, name='create_testimonial'),
    path('api/testimonials/update/', views.update_testimonial, name='update_testimonial'),
    path('api/testimonials/my-review/', views.get_user_testimonial, name='get_user_testimonial'),
    path('api/google-reviews/', views.google_reviews_api, name='google_reviews_api'),
    
    # Razorpay-compliant Policy Pages
    path('terms-and-conditions/', views.TermsConditionsView.as_view(), name='terms_conditions'),
    path('cancellation-refund-policy/', views.CancelRefundPolicyView.as_view(), name='cancel_refund_policy'),
    path('privacy-policy/', views.PrivacyPolicyView.as_view(), name='privacy_policy'),
    path('shipping-policy/', views.ShippingPolicyView.as_view(), name='shipping_policy'),
    path('disclaimer-policy/', views.DisclaimerPolicyView.as_view(), name='disclaimer_policy'),
    path('razorpay-privacy-policy/', views.RazorpayPrivacyPolicyView.as_view(), name='razorpay_privacy_policy'),
]

