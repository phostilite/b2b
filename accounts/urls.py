from django.urls import path

from . import views

urlpatterns = [
    path('', views.landing_page, name='landing_page'),
    path('forgot-username/', views.forgot_username, name='forgot_username'),
]