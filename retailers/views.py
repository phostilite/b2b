from django.shortcuts import render
import logging
from django.shortcuts import render, redirect

from .models import Retailer
from .forms import RetailerForm

from accounts.decorators import allowed_users
from django.contrib.auth.decorators import login_required

logger = logging.getLogger(__name__)

@login_required
@allowed_users(allowed_roles=["Admin", "Sales", "Dealer"])
def retailer_list_view(request):

    if request.user.groups.filter(name='Admin').exists():
        retailers = Retailer.objects.all()
        return render(request, 'admin/retailer_list.html', {'retailers': retailers})
    elif request.user.groups.filter(name='Sales').exists():
        retailers = Retailer.objects.all()
        return render(request, 'employee/retailer_list.html', {'retailers': retailers})
    elif request.user.groups.filter(name='Dealer').exists():
        retailers = Retailer.objects.filter(created_by=request.user)
        return render(request, 'dealer/retailer_list.html', {'retailers': retailers})

@login_required
@allowed_users(allowed_roles=["Admin", "Sales", "Dealer"])
def create_retailer(request):
    if request.method == 'POST':
        form = RetailerForm(request.POST)
        if form.is_valid():
            if request.user.is_authenticated:
                retailer = form.save(commit=False)
                retailer.created_by = request.user
                retailer.save()
                return redirect('retailer_list')
            else:
                return redirect('login')
        else:
            logger.error(f'RetailerForm errors: {form.errors}')
    else:
        form = RetailerForm()

    if request.user.groups.filter(name='Admin').exists():
        return render(request, 'admin/create_retailer.html', {'form': form})
    elif request.user.groups.filter(name='Dealer').exists():
        return render(request, 'dealer/create_retailer.html', {'form': form})
    elif request.user.groups.filter(name='Sales').exists():
        return render(request, 'employee/create_retailer.html', {'form': form})