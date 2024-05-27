import random
from django.core.mail import send_mail
from django.conf import settings

def generate_otp():
    """Generate a 6-digit OTP."""
    return random.randint(100000, 999999)

def send_otp(dealer):
    """Generate an OTP and send it to the dealer's email."""
    otp = generate_otp()
    send_mail(
        'Your OTP for Agreement Signing',
        f'Dear {dealer.user.first_name},\n\n'
        'You have requested to sign the agreement. '
        'Please use the following One-Time Password (OTP) to proceed:\n\n'
        f'{otp}\n\n'
        'This OTP is valid for a short period of time for security reasons. '
        'If it expires, please request a new one.\n\n'
        'Best regards,\n'
        'Itease B2B Platform Team\n',
        settings.DEFAULT_FROM_EMAIL,
        [dealer.user.email],
    )
    return otp

def verify_otp(session_otp, user_otp):
    """Verify the OTP entered by the user."""
    return session_otp == int(user_otp)