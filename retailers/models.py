from django.db import models

class Retailer(models.Model):
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    address = models.TextField()
    pincode = models.CharField(max_length=10)
    contact_number = models.CharField(max_length=20)
    email = models.EmailField(null=True, blank=True)
    gstin = models.CharField(max_length=20, null=True, blank=True)
    created_by = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='retailers', null=True, blank=True)
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.first_name + ' ' + self.last_name