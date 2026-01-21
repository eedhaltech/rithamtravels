from django.urls import path
from . import views

urlpatterns = [
    path('api/bookings/', views.create_booking, name='create_booking'),
    path('api/bookings/summary/', views.get_booking_summary, name='get_booking_summary'),
    path('api/bookings/status/<str:booking_number>/', views.get_booking_status, name='get_booking_status'),
    path('api/bookings/validate-payment/', views.validate_booking_for_payment, name='validate_booking_for_payment'),
    path('api/bookings/process-payment/', views.process_payment, name='process_payment'),
    path('api/bookings/payment-success/', views.payment_success, name='payment_success'),
    path('api/bookings/verify-cancellation/', views.verify_booking_for_cancellation, name='verify_booking_for_cancellation'),
    path('api/bookings/confirm-cancellation/', views.confirm_cancellation, name='confirm_cancellation'),
    path('api/bookings/online-booking/', views.create_online_booking, name='create_online_booking'),
    path('api/razorpay/order/', views.create_razorpay_order, name='create_razorpay_order'),
    path('api/razorpay/callback/', views.razorpay_callback, name='razorpay_callback'),
    # WhatsApp Webhook
    path('webhook/whatsapp/', views.whatsapp_webhook, name='whatsapp_webhook'),
    # Notification testing and monitoring
    path('api/notifications/trigger/', views.trigger_booking_notification, name='trigger_booking_notification'),
    path('api/notifications/status/', views.notification_service_status, name='notification_service_status'),
    # Template views
    path('payment/', views.PaymentPageView.as_view(), name='payment'),
    path('payment/success/', views.payment_success_page, name='payment_success_page'),
    path('cancellation/', views.CancellationPageView.as_view(), name='cancellation'),
    path('online-cab-booking/', views.OnlineCabBookingView.as_view(), name='online_cab_booking'),
    path('booking/', views.BookingPageView.as_view(), name='booking'),
    path('booking-status/', views.BookingStatusView.as_view(), name='booking_status'),
    path('booking-confirmation/<str:booking_number>/', views.booking_confirmation, name='booking_confirmation'),
    path('booking/<int:booking_id>/', views.booking_details, name='booking_details'),
]

