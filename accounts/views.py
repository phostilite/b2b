from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings

def landing_page(request):
    if request.user.is_authenticated:
        if request.user.groups.filter(name='Admin').exists():
            return redirect('admin_dashboard')
        elif request.user.groups.filter(name='Dealer').exists():
            return redirect('dealer_dashboard')
    return redirect('dealer_login')

def forgot_username(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
            subject = 'Your Username on Itease B2B Platform'
            message = f'Dear {user.first_name},\n\n'
            message += 'You recently requested your username for the Itease B2B Platform. Your username is:\n\n'
            message += f'{user.username}\n\n'
            message += 'This username is associated with the email address you provided.\n\n'
            message += 'If you did not initiate this request, please contact our support team immediately for assistance.\n\n'
            message += 'Thank you for using our platform.\n\n'
            message += 'Best regards,\n'
            message += 'Itease B2B Platform Team'
            from_email = settings.DEFAULT_FROM_EMAIL
            recipient_list = [email]
            send_mail(subject, message, from_email, recipient_list, fail_silently=False)
            return render(request, 'registration/forgot_username_sent.html')
        except User.DoesNotExist:
            return render(request, 'registration/forgot_username_error.html', {'error': 'Email not found.'})
    return render(request, 'registration/forgot_username.html')