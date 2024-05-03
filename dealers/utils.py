import random
from twilio.rest import Client
from django.core.mail import send_mail
from django.conf import settings

def generate_otp():
    """Generate a 6-digit OTP."""
    return random.randint(100000, 999999)

def send_otp(dealer):
    """Generate an OTP and send it to the dealer's phone and email."""
    otp = generate_otp()

    # Send OTP via SMS
    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN1)
    message = client.messages.create(
        body=f'Your OTP is {otp}',
        from_=settings.TWILIO_PHONE_NUMBER,
        to=dealer.phone,  # Make sure this is in E.164 format
    )

    # Send OTP via email
    send_mail(
        'Your OTP',
        f'Your OTP is {otp}',
        settings.DEFAULT_FROM_EMAIL,
        [dealer.user.email],
    )

    return otp

def verify_otp(session_otp, user_otp):
    """Verify the OTP entered by the user."""
    return session_otp == int(user_otp)