from django.db import models
from django.contrib.auth.models import User

class Dealer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100, null=True, blank=True)
    last_name = models.CharField(max_length=100, null=True, blank=True)
    full_name = models.CharField(max_length=200, blank=True)
    phone = models.CharField(max_length=13)
    email = models.EmailField(null=True, blank=True)
    agreement_accepted = models.BooleanField(default=False)
    profile_pic = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    
    def __str__(self):
        return f"{self.full_name}"
        
class Document(models.Model):
    dealer = models.ForeignKey('Dealer', on_delete=models.CASCADE, related_name='documents')
    document_type = models.CharField(max_length=50)
    file = models.FileField(upload_to='documents/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.dealer} - {self.document_type}"