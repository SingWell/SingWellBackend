from django.db import models

# Create your models here.
class Organization(models.Model):
    name = models.CharField(max_length=50, blank=False, null=False)
    address = models.CharField(max_length=50, blank=False, null=False)
    contact_phone_number = models.CharField(max_length=20, null=True)
    contact_email = models.CharField(max_length=350, null=False, blank=False)
    description = models.TextField()
    created_date = models.DateTimeField(auto_now_add=True)
