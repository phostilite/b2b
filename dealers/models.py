from django.db import models
from django.contrib.auth.models import User

class Dealer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=200, blank=True)
    phone = models.CharField(max_length=13)
    email = models.EmailField(null=True, blank=True)
    agreement_accepted = models.BooleanField(default=False)
    profile_pic = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    gstin = models.CharField(max_length=15, null=True, blank=True)
        
    def __str__(self):
        return f"{self.full_name}"
    
class Address(models.Model):
    dealer = models.ForeignKey('Dealer', on_delete=models.CASCADE, related_name='addresses')
    address_line_1 = models.CharField(max_length=200)
    address_line_2 = models.CharField(max_length=200, blank=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100, default='India')
    zip_code = models.CharField(max_length=10)
    
    def __str__(self):
        return f"{self.dealer} - {self.address_line_1}"
        
class Document(models.Model):
    dealer = models.ForeignKey('Dealer', on_delete=models.CASCADE, related_name='documents')
    document_type = models.CharField(max_length=50)
    file = models.FileField(upload_to='documents/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.dealer} - {self.document_type}"