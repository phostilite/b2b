from django.shortcuts import render, redirect
from django.contrib.auth.models import Group
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages

from accounts.decorators import allowed_users
from django.contrib.auth.decorators import login_required

from .forms import AdminUserProfileForm

@login_required
@allowed_users(allowed_roles=["Admin"])
def admin_dashboard_view(request):
    return render(request, 'admin/dashboard.html')

def admin_login_view(request):
    form_errors = []

    if request.user.is_authenticated and request.user.groups.filter(name='Admin').exists():
        messages.success(request, 'You are already logged in.')
        return redirect('admin_dashboard')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, 'Login successful. Welcome to the admin dashboard.')
            return redirect('admin_dashboard')
        else:
            form_errors.append('Username or Password: Invalid username or password.')

    return render(request, 'authentication/admin_login.html', {'form_errors': form_errors})

def admin_logout_view(request):
    logout(request)
    return redirect('admin_login')

login_required
def update_profile(request):
    if request.method == 'POST':
        form = AdminUserProfileForm(request.POST, request.FILES, instance=request.user.adminuser)
        if form.is_valid():
            adminuser = form.save(commit=False)
            adminuser.user.first_name = adminuser.first_name
            adminuser.user.last_name = adminuser.last_name
            adminuser.user.email = adminuser.email
            adminuser.user.save()
            adminuser.save()
            messages.success(request, 'Your profile was successfully updated!')
            return redirect('adminuser_profile')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = AdminUserProfileForm(instance=request.user.adminuser)
    return render(request, 'admin/profile.html', {
        'form': form
    })