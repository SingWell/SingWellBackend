from api.models import Organization, Choir
from api.serializers import OrganizationSerializer, UserSerializer, ChoirSerializer
from django.contrib.auth.models import User

user = User.objects.create_user("bob", "bob@smu.edu", "password123")
user.first_name = "Bob"
user.last_name = "Johnson"
user.save()

user2 = User.objects.create_user("sally", "sally@smu.edu", "password123")
user2.first_name = "Sally"
user2.last_name = "Singwell"
user2.save()

org = Organization.objects.create(name="Test Org", address="123 address",
                                  description="Test Organization", owner=user)
org.save()

choir = Choir.objects.create(name="Traditional Choir", meeting_day=2, meeting_day_start_time="11:00:00am", organization=org)
choir.save()