from django.db import models
from django import forms
from django.contrib.auth.models import User


	

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
    description = models.TextField()
    created_date = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(User, related_name="owned_organizations")
    admins = models.ManyToManyField(User, related_name="admin_of_organizations")

    def __str__(self):
        return f"{self.name}, owned by {self.owner.first_name} {self.owner.last_name}"


class Choir(models.Model):
    organization = models.OneToOneField(Organization)
    name = models.CharField(max_length=50, null=False, blank=False)
    meeting_day = models.IntegerField(choices=WEEKDAYS, null=False, blank=False)
    meeting_day_start_hour = models.TimeField(null=False)
    meeting_day_end_hour = models.TimeField(null=True)

    # perform_day = models.IntegerField(choices=WEEKDAYS, null=True, blank=True)
    # perform_day_start_hour = models.TimeField(null=True)
    # perform_day_end_hour = models.TimeField()

    choristers = models.ManyToManyField(User)

    def __str__(self):
        return f"{self.name}, meets on {self.meeting_day} at {self.meeting_day_start_hour}"


class Talents(models.Model):
    name = models.CharField(max_length=50, null=False, blank=False)
    user = models.ForeignKey(User)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}, {self.name}"


class UserProfile(models.Model):
    user = models.OneToOneField(User, related_name="profile")
    bio = models.CharField(max_length=255, null=True)
    address = models.CharField(max_length=100, null=True)
    city = models.CharField(max_length=100, null=True)
    zip_code = models.CharField(max_length=5, null=True)
    phone_number = models.CharField(max_length=10, null=True)
    state = models.CharField(max_length=20, null=True)
    date_of_birth = models.DateField(null=True, blank=True)