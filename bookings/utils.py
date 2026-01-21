from django.core.mail import send_mail
from django.conf import settings
import requests


def send_booking_confirmation_email(booking):
    subject = f'Booking Confirmation - {booking.booking_number}'
    
    # Build comprehensive booking details
    trip_type_display = booking.get_trip_type_display() if hasattr(booking, 'get_trip_type_display') else booking.trip_type
    
    # Vehicle details
    vehicle_info = ""
    if booking.vehicle:
        vehicle_info = f"""
Vehicle Details:
- Vehicle: {booking.vehicle.display_name}
- Seating Capacity: {booking.vehicle.seating_info}
- Fuel Type: {booking.vehicle.get_fuel_type_display()}
- Fare per KM: ₹{booking.vehicle.fare_per_km}
"""
    
    # Passenger details
    passenger_info = f"""
Passenger Details:
- Adults: {booking.adults}
- Children: {booking.children}
- Total Passengers: {booking.adults + booking.children}
"""
    
    # Address details
    address_info = f"""
Trip Details:
- Pickup Address: {booking.pickup_address or 'Not specified'}
- Drop Address: {booking.drop_address or 'Not specified'}
- Pickup Date: {booking.pickup_date or 'Not specified'}
- Pickup Time: {booking.pickup_time or 'Not specified'}
"""
    
    # Add drop date/time if available
    if booking.drop_date:
        address_info += f"- Drop Date: {booking.drop_date}\n"
    if booking.drop_time:
        address_info += f"- Drop Time: {booking.drop_time}\n"
    
    # Flight/Train details if provided
    additional_info = ""
    if booking.flight_train_no:
        additional_info += f"- Flight/Train Number: {booking.flight_train_no}\n"
    if booking.landmark:
        additional_info += f"- Landmark: {booking.landmark}\n"
    if booking.special_instructions:
        additional_info += f"- Special Instructions: {booking.special_instructions}\n"
    
    # Payment details - special handling for online cab booking
    payment_info = f"""
Payment Information:
- Payment Method: {booking.get_payment_type_display() if hasattr(booking, 'get_payment_type_display') else booking.payment_type}
"""
    
    # For online cab booking, don't show amount as it will be calculated by admin
    if booking.trip_type == 'online_cab':
        payment_info += "- Fare: To be calculated based on actual distance and time\n"
        payment_info += "- Our team will contact you with fare details before the trip\n"
    else:
        payment_info += f"- Total Amount: ₹{booking.total_amount}\n"
        if booking.advance_amount and booking.advance_amount > 0:
            payment_info += f"- Advance Paid: ₹{booking.advance_amount}\n"
            remaining = float(booking.total_amount) - float(booking.advance_amount)
            if remaining > 0:
                payment_info += f"- Remaining Amount: ₹{remaining:.2f}\n"
    
    # Trip specific details
    trip_details = ""
    if booking.total_days and booking.total_days > 1:
        trip_details += f"- Total Days: {booking.total_days}\n"
    if booking.total_distance and booking.total_distance > 0:
        trip_details += f"- Total Distance: {booking.total_distance} KM\n"
    
    # Customize message based on trip type
    if booking.trip_type == 'online_cab':
        main_message = f"""
Dear {booking.name},

Thank you for your online cab booking request with {settings.COMPANY_NAME}!

ONLINE CAB BOOKING REQUEST
==========================

Your booking request has been received and our team will contact you shortly with fare details and confirmation.

Booking Number: {booking.booking_number}
Trip Type: {trip_type_display}
"""
        closing_message = """
NEXT STEPS:
===========
- Our team will calculate the fare based on your trip details
- You will receive a call within 30 minutes with fare confirmation
- Upon your approval, we will confirm the booking and assign a driver
- Driver details will be shared 1 hour before pickup time

"""
    else:
        main_message = f"""
Dear {booking.name},

Thank you for booking with {settings.COMPANY_NAME}!

BOOKING CONFIRMATION
====================

Booking Number: {booking.booking_number}
Trip Type: {trip_type_display}
"""
        closing_message = """
IMPORTANT NOTES:
================
- Please arrive at the pickup location 10 minutes before the scheduled time
- Driver contact details will be shared 1 hour before pickup
- For any changes or cancellations, please contact us immediately
- Carry a valid ID proof during travel
- Our driver will contact you upon arrival at pickup location

"""

    message = main_message + f"""
{passenger_info}
{address_info}
{vehicle_info}
{payment_info}
{trip_details}
{additional_info}

{closing_message}
CONTACT INFORMATION:
===================
Phone: +91 97871 10763
Email: info@rithamtravels.in
WhatsApp: +91 97871 10763

We look forward to serving you and making your journey comfortable!

Best regards,
{settings.COMPANY_NAME}
Team Ritham Tours & Travels
"""
    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [booking.email],
            fail_silently=False,
        )
    except Exception as e:
        print(f"Email sending failed: {e}")


def send_booking_whatsapp(booking):
    """Send WhatsApp notification using API"""
    trip_type_display = booking.get_trip_type_display() if hasattr(booking, 'get_trip_type_display') else booking.trip_type
    
    # Build comprehensive WhatsApp message
    vehicle_name = booking.vehicle.display_name if booking.vehicle else "Vehicle TBD"
    
    if booking.trip_type == 'online_cab':
        message = f"""
🚗 *ONLINE CAB BOOKING REQUEST RECEIVED!*

📋 *Request Details:*
Booking No: *{booking.booking_number}*
Trip Type: {trip_type_display}
Vehicle: {vehicle_name}

👥 *Passengers:*
Adults: {booking.adults} | Children: {booking.children}

📍 *Trip Information:*
Pickup: {booking.pickup_address or 'Not specified'}
Drop: {booking.drop_address or 'Not specified'}
Date: {booking.pickup_date or 'TBD'}
Time: {booking.pickup_time or 'TBD'}

💰 *Payment:*
Method: {booking.get_payment_type_display() if hasattr(booking, 'get_payment_type_display') else booking.payment_type}
Fare: *To be calculated and confirmed*

⏰ *Next Steps:*
• Our team will call you within 30 minutes
• Fare will be calculated based on actual distance
• Booking confirmation upon your approval
"""
    else:
        message = f"""
🎉 *BOOKING CONFIRMED!*

📋 *Booking Details:*
Booking No: *{booking.booking_number}*
Trip Type: {trip_type_display}
Vehicle: {vehicle_name}

👥 *Passengers:*
Adults: {booking.adults} | Children: {booking.children}

📍 *Trip Information:*
Pickup: {booking.pickup_address or 'Not specified'}
Drop: {booking.drop_address or 'Not specified'}
Date: {booking.pickup_date or 'TBD'}
Time: {booking.pickup_time or 'TBD'}

💰 *Payment:*
Method: {booking.get_payment_type_display() if hasattr(booking, 'get_payment_type_display') else booking.payment_type}
Total: ₹{booking.total_amount}
"""
        
        if booking.advance_amount and booking.advance_amount > 0:
            message += f"Advance Paid: ₹{booking.advance_amount}\n"
    
    if booking.special_instructions:
        message += f"\n📝 *Instructions:* {booking.special_instructions}\n"
    
    message += f"""
📞 *Contact Us:*
Phone: +91 97871 10763
WhatsApp: +91 97871 10763

Thank you for choosing *{settings.COMPANY_NAME}*! 🚗✨
"""
    
    # Implement WhatsApp API integration here
    # This is a placeholder - you'll need to integrate with Twilio, WhatsApp Business API, etc.
    pass


def send_admin_notification(booking):
    """Send notification to admin about new booking"""
    subject = f'New Booking Received - {booking.booking_number}'
    
    # Build comprehensive admin notification
    trip_type_display = booking.get_trip_type_display() if hasattr(booking, 'get_trip_type_display') else booking.trip_type
    
    if booking.trip_type == 'online_cab':
        subject = f'New Online Cab Booking Request - {booking.booking_number}'
        message_header = "NEW ONLINE CAB BOOKING REQUEST"
        payment_section = f"""
PAYMENT:
Method: {booking.get_payment_type_display() if hasattr(booking, 'get_payment_type_display') else booking.payment_type}
Fare: TO BE CALCULATED

ACTION REQUIRED:
1. Calculate fare based on pickup/drop locations
2. Call customer to confirm fare and booking
3. Assign driver upon customer approval
"""
    else:
        subject = f'New Booking Received - {booking.booking_number}'
        message_header = "NEW BOOKING ALERT"
        payment_section = f"""
PAYMENT:
Method: {booking.get_payment_type_display() if hasattr(booking, 'get_payment_type_display') else booking.payment_type}
Total: ₹{booking.total_amount}
Advance: ₹{booking.advance_amount or 0}

ACTION REQUIRED:
Please assign driver and confirm the booking.
"""
    
    # Vehicle details
    vehicle_info = ""
    if booking.vehicle:
        vehicle_info = f"""
Vehicle: {booking.vehicle.display_name}
Seating: {booking.vehicle.seating_info}
Fare/KM: ₹{booking.vehicle.fare_per_km}
"""
    
    # Address details
    address_info = f"""
Pickup: {booking.pickup_address or 'Not specified'}
Drop: {booking.drop_address or 'Not specified'}
Pickup Date: {booking.pickup_date or 'Not specified'}
Pickup Time: {booking.pickup_time or 'Not specified'}
"""
    
    if booking.drop_date:
        address_info += f"Drop Date: {booking.drop_date}\n"
    if booking.drop_time:
        address_info += f"Drop Time: {booking.drop_time}\n"
    
    # Additional details
    additional_info = ""
    if booking.flight_train_no:
        additional_info += f"Flight/Train: {booking.flight_train_no}\n"
    if booking.landmark:
        additional_info += f"Landmark: {booking.landmark}\n"
    if booking.special_instructions:
        additional_info += f"Instructions: {booking.special_instructions}\n"
    
    # Trip details
    trip_details = ""
    if booking.total_days and booking.total_days > 1:
        trip_details += f"Days: {booking.total_days}\n"
    if booking.total_distance and booking.total_distance > 0:
        trip_details += f"Distance: {booking.total_distance} KM\n"
    
    message = f"""
{message_header}
=================

Booking Number: {booking.booking_number}
Trip Type: {trip_type_display}

CUSTOMER DETAILS:
Name: {booking.name}
Email: {booking.email}
Phone: {booking.phone}
Adults: {booking.adults}
Children: {booking.children}

TRIP DETAILS:
{address_info}
{vehicle_info}
{trip_details}

{payment_section}

{additional_info}
"""
    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [settings.COMPANY_EMAIL],
            fail_silently=False,
        )
    except Exception as e:
        print(f"Admin notification failed: {e}")


def send_payment_confirmation_email(payment):
    """Send payment confirmation email"""
    booking = payment.booking
    subject = f'Payment Confirmation - {booking.booking_number}'
    message = f"""
Dear {booking.name},

Your payment has been successfully processed!

Payment Details:
- Payment ID: {payment.razorpay_payment_id}
- Booking Number: {booking.booking_number}
- Amount Paid: ₹{payment.amount}
- Payment Date: {payment.created_at.strftime('%d %B %Y, %I:%M %p')}

Thank you for your payment!

Best regards,
{settings.COMPANY_NAME}
{settings.COMPANY_PHONE}
"""
    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [booking.email],
            fail_silently=False,
        )
    except Exception as e:
        print(f"Payment confirmation email failed: {e}")


def send_payment_whatsapp(payment):
    """Send WhatsApp notification for payment"""
    booking = payment.booking
    message = f"""
Payment Confirmed! ✅

Payment ID: {payment.razorpay_payment_id}
Booking Number: {booking.booking_number}
Amount Paid: ₹{payment.amount}

Thank you for your payment!
{settings.COMPANY_NAME}
"""
    # Implement WhatsApp API integration here
    pass


def send_cancellation_confirmation_email(booking, refund_amount, refunded_payments):
    """Send cancellation confirmation email"""
    subject = f'Booking Cancellation - {booking.booking_number}'
    refund_info = f"Refund Amount: ₹{refund_amount:.2f}\n" if refund_amount > 0 else "No refund applicable.\n"
    if refunded_payments:
        refund_info += "\nRefund Details:\n"
        for rp in refunded_payments:
            refund_info += f"- Payment ID: {rp['payment_id']}, Refund ID: {rp['refund_id']}, Amount: ₹{rp['amount']:.2f}\n"
    
    message = f"""
Dear {booking.name},

Your booking has been cancelled successfully.

Booking Details:
- Booking Number: {booking.booking_number}
- Trip Type: {booking.get_trip_type_display()}
- Pickup Date: {booking.pickup_date}
- Total Amount: ₹{booking.total_amount}

{refund_info}

If you have any questions, please contact us.

Best regards,
{settings.COMPANY_NAME}
{settings.COMPANY_PHONE}
"""
    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [booking.email],
            fail_silently=False,
        )
    except Exception as e:
        print(f"Cancellation confirmation email failed: {e}")


def send_cancellation_whatsapp(booking, refund_amount):
    """Send WhatsApp notification for cancellation"""
    message = f"""
Booking Cancelled ❌

Booking Number: {booking.booking_number}
Trip Type: {booking.get_trip_type_display()}
Refund Amount: ₹{refund_amount:.2f}

Thank you for choosing {settings.COMPANY_NAME}!
"""
    # Implement WhatsApp API integration here
    pass

