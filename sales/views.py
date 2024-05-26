import logging

from django.shortcuts import render, redirect
from django.contrib.auth.models import Group
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages

from .models import Employee
from .forms import EmployeeForm, EmployeeProfileForm
from accounts.decorators import allowed_users
from django.contrib.auth.decorators import login_required

logger = logging.getLogger(__name__)

@login_required
@allowed_users(allowed_roles=["Sales"])
def employee_dashboard_view(request):
    return render(request, 'employee/dashboard.html')

def employee_login_view(request):
    form_errors = []

    try:
        if request.user.is_authenticated and request.user.groups.filter(name='Sales').exists():
            messages.success(request, 'You are already logged in.')
            return redirect('employee_dashboard')
        
        if request.method == 'POST':
            username = request.POST.get('username')
            password = request.POST.get('password')

            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('employee_dashboard')
            else:
                form_errors.append('Username or Password: Invalid username or password.')
        return render(request, 'authentication/sales_login.html', {'form_errors': form_errors})
    except Exception as e:
        logger.error(f'An error occurred in employee_login_view: {e}')
        return render(request, 'authentication/sales_login.html', {'form_errors': form_errors})

def employee_logout_view(request):
    logout(request)
    return redirect('employee_login')

@login_required
@allowed_users(allowed_roles=["Admin"])
def employee_list_view(request):
    employees = Employee.objects.all()
    return render(request, 'admin/employee_list.html', {'employees': employees})

@login_required
@allowed_users(allowed_roles=["Admin"])
def create_employee(request):
    if request.method == 'POST':
        form = EmployeeForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('employee_list')
        else:
            logger.error(f'EmployeeForm errors: {form.errors}')
    else:
        form = EmployeeForm()
    return render(request, 'admin/create_employee.html', {'form': form})

login_required
def update_profile(request):
    if request.method == 'POST':
        form = EmployeeProfileForm(request.POST, request.FILES, instance=request.user.employee)
        if form.is_valid():
            employee = form.save(commit=False)
            employee.user.first_name = employee.full_name.split(' ')[0]
            employee.user.last_name = employee.full_name.split(' ')[1]
            employee.user.email = employee.email
            employee.user.save()
            employee.save()
            messages.success(request, 'Your profile was successfully updated!')
            return redirect('employee_profile')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = EmployeeProfileForm(instance=request.user.employee)
    return render(request, 'employee/profile.html', {
        'form': form
    })