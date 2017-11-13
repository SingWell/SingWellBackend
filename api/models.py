from django.db import models
from django import forms
from django.contrib.auth.models import User
from localflavor.us.forms import USStateField, USZipCodeField, USPhoneNumberField


	

#Used to identify choir meeting times
WEEKDAYS = [
  (1, ("Monday")),
  (2, ("Tuesday")),
  (3, ("Wednesday")),
  (4, ("Thursday")),
  (5, ("Friday")),
  (6, ("Saturday")),
  (7, ("Sunday")),
]


# Create your models here.
class Organization(models.Model):
    name = models.CharField(max_length=50, blank=False, null=False)
    address = models.CharField(max_length=50, blank=False, null=False)
    contact_phone_number = models.CharField(max_length=20, null=True)
    contact_email = models.CharField(max_length=350, null=False, blank=False)
    description = models.TextField()
    created_date = models.DateTimeField(auto_now_add=True)


class Choir(models.Model):
    name = models.CharField(max_length=50, null=False, blank=False)
    meeting_day = models.IntegerField(choices=WEEKDAYS, null=False, blank=False)
    meeting_day_start_hour = models.TimeField(null=False)
    meeting_day_end_hour = models.TimeField()
    
    perform_day = models.IntegerField(choices=WEEKDAYS, null=False, blank=False)
    perform_day_start_hour = models.TimeField(null=False)
    perform_day_end_hour = models.TimeField()

    choristers = models.ManyToManyField(User)

class Talents(models.Model):
    name = models.CharField(max_length=50, null=False, blank=False)
    user = models.ForeignKey(User)

class UserProfile(models.Model):
    user = models.OneToOneField(User, related_name="profile")
    address = models.CharField(max_length =100, null=True)
    city = models.CharField(max_length =100, null=True)
    zip_code = USZipCodeField()
    phone_number = USPhoneNumberField()
    state = USStateField()
