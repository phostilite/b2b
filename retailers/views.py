from django.shortcuts import render
import logging
from django.shortcuts import render, redirect

from .models import Retailer
from .forms import RetailerForm

from accounts.decorators import allowed_users
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseServerError
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404

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
    
@require_POST
@login_required
def delete_retailer_view(request, retailer_id):
    try:
        retailer = get_object_or_404(Retailer, pk=retailer_id)
        retailer.delete()
        logger.info('Reatiler with id %s deleted successfully', retailer_id)
        return JsonResponse({'status': 'success', 'message': 'Reatiler deleted successfully'})
    except Exception as e:
        logger.error('An error occurred while deleting the retailer with id %s: %s', retailer_id, str(e))
        return HttpResponseServerError({'status': 'error', 'message': 'An error occurred while deleting the retailer: ' + str(e)})