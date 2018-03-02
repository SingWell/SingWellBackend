from django.db import models
from django.contrib.auth.models import User
from datetime import datetime

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

# __str__ is used in the HTML
# __unicode__ is used more internally

# class Address(models.Model):
#     street = models.CharField(max_length=300, null=True)
#     city = models.CharField(max_length=100, null=True)
#     state = models.CharField(max_length=20, null=True)
#     zipcode = models.CharField(max_length=20, null=True)

class Organization(models.Model):
    name = models.CharField(max_length=50, blank=False, null=False)
    address = models.CharField(max_length=50, blank=False, null=True)
    phone_number = models.CharField(max_length=20, null=True)
    email = models.CharField(max_length=300, null=True)
    description = models.TextField(null=True)
    created_date = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(User, related_name="owned_organizations")
    admins = models.ManyToManyField(User, related_name="admin_of_organizations")

    website_url = models.CharField(max_length=2000, blank=True, null=True)

    def __str__(self):
        return f"{self.name}, owned by {self.owner.first_name} {self.owner.last_name}"

    def __unicode__(self):
        return f"{self.name}"


class Choir(models.Model):
    organization = models.ForeignKey(Organization)
    name = models.CharField(max_length=50, null=False, blank=False)
    meeting_day = models.IntegerField(choices=WEEKDAYS, null=False, blank=False)
    meeting_day_start_hour = models.TimeField(null=False)
    meeting_day_end_hour = models.TimeField(null=True)
    description = models.TextField(null=True, blank=True)

    # perform_day = models.IntegerField(choices=WEEKDAYS, null=True, blank=True)
    # perform_day_start_hour = models.TimeField(null=True)
    # perform_day_end_hour = models.TimeField()

    choristers = models.ManyToManyField(User, related_name="choirs")

    @property
    def organization_name(self):
        return self.organization.name

    def __str__(self):
        return f"{self.name}, meets on {self.meeting_day} at {self.meeting_day_start_hour}"

    def __unicode__(self):
        return f"{self.name}"


class Talents(models.Model):
    name = models.CharField(max_length=50, null=False, blank=False)
    user = models.ForeignKey(User)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}, {self.name}"

    def __unicode__(self):
        return f"{self.name}"


class UserProfile(models.Model):
    user = models.OneToOneField(User, related_name="profile")
    bio = models.CharField(max_length=255, null=True)
    address = models.CharField(max_length=100, null=True)
    city = models.CharField(max_length=100, null=True)
    zip_code = models.CharField(max_length=5, null=True)
    phone_number = models.CharField(max_length=10, null=True)
    state = models.CharField(max_length=20, null=True)
    date_of_birth = models.DateField(null=True, blank=True)
    @property
    def age(self):
        return datetime.today().year - self.date_of_birth.year - ((datetime.today().month, datetime.today().day) < (self.date_of_birth.month, self.date_of_birth.day))


class Event(models.Model):
    name = models.CharField(max_length=200, null=False, blank=False)
    date = models.DateField(null=False, blank=False)
    time = models.TimeField(null=True)
    location = models.CharField(max_length=200, null=True, blank=True)
    choirs = models.ManyToManyField(Choir, related_name="events")
    program_music = models.ManyToManyField("MusicRecord", through="ProgramField")

    organization = models.ForeignKey(Organization)

    def __str__(self):
        return f"{self.name} on {self.date} at {self.time}"

    def __unicode__(self):
        return f"{self.name}"


class ProgramField(models.Model):
    event = models.ForeignKey(Event)
    music_record = models.ForeignKey("MusicRecord")
    order = models.IntegerField()
    notes = models.CharField(max_length=2000, null=True)

    def __str__(self):
        return f"{self.music_record.title}, event: {self.event.name}, order: {self.order}"

    class Meta:
        unique_together = (('order', 'music_record', 'event'),)


class MusicRecord(models.Model):
    title = models.CharField(max_length=500, null=False, blank=False)
    composer = models.CharField(max_length=200, null=True, blank=True)
    arranger = models.CharField(max_length=200, null=True, blank=True)
    publisher = models.CharField(max_length=200, null=True, blank=True)
    instrumentation = models.CharField(max_length=500, null=True, blank=True)

    organization = models.ForeignKey(Organization)

    def __str__(self):
        return f"{self.title}, owned by {self.organization.name}"

    def __unicode__(self):
        return f"{self.title}"


class MusicResource(models.Model):
    """Represents a basic resource, a type and data that goes in that type"""
    type = models.CharField(max_length=100, null=False, blank=False)
    title = models.CharField(max_length= 100, null=False,blank=False, default='Title')
    music_record = models.ForeignKey(MusicRecord)
    # class Meta:
    #     abstract=True
class FileResource(MusicResource):
    file_name = models.CharField(max_length=300, null=False, blank=False)
    file_type = models.CharField(max_length=10, null=False, blank=False)
    def _get_class(self):
        return self.__class__

class TextResource(MusicResource):
    field = models.CharField(max_length=3000, null=False, blank=False)
    def _get_class(self):
        return self.__class__  