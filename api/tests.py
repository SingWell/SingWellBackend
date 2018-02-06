from django.test import TestCase, Client
from api.models import *
from api.serializers import *

c = Client()

class UserTestCase(TestCase):
    def setUp(self):
        data = {
            "email"   : "joien@smu.edu",
            "password": "password",
            "username": "jake",
            "first_name": "Jake",
            "last_name": "Oien"
            }
        ser = UserSerializer()
        ser.create(validated_data=data)

    def test_userCreated(self):
        user = User.objects.get(email="joien@smu.edu")
        self.assertEquals(user.email, "joien@smu.edu", "test message")

    def test_onlyEmailAndPasswordAreRequiredToCreateUser(self):
        response = c.post("/users/", {"email": "jake@smu.edu", "password": "password"})
        self.assertIn(response.status_code, [200, 201])


class OrganizationTestCase(TestCase):
    def setUp(self):
        userData = {
            "email"   : "joien@smu.edu",
            "password": "password",
            "username": "jake",
            "first_name": "Jake",
            "last_name": "Oien"
            }

        ser = UserSerializer()
        ser.create(validated_data=userData)

        org_data = {
            "name": "Setup Org",
            "owner": User.objects.get(email="joien@smu.edu")
            }

        OrganizationSerializer().create(validated_data=org_data)

    def test_canPostOrganization(self):
        print(User.objects.all())
        user_id = User.objects.get(email="joien@smu.edu").id
        data = {
            "name": "Test organization",
            "owner": user_id
            }
        response = c.post("/organizations/", data)

        self.assertEqual(response.status_code, 201)

    def test_canPatchOrganization(self):
        org = Organization.objects.get(name="Setup Org")
        org_id = org.id

        response = c.patch(f"/organizations/{org_id}/", data='{"description": "hi"}', content_type="application/json")
        self.assertIn(response.status_code, [200,204])


class EventTestCase(TestCase):
    def setUp(self):
        userData = {
            "email"     : "joien@smu.edu",
            "password"  : "password",
            "username"  : "jake",
            "first_name": "Jake",
            "last_name" : "Oien"
            }

        ser = UserSerializer()
        ser.create(validated_data=userData)

        org_data = {
            "name" : "Setup Org",
            "owner": User.objects.get(email="joien@smu.edu")
            }

        OrganizationSerializer().create(validated_data=org_data)

    def test_canPostEventWithRequiredFields(self):
        org = Organization.objects.get(name="Setup Org")
        data = {
            "name": "Sunday Mass",
            "date": "2018-01-01",
            "organization": org.id
            }

        response = c.post(f"/events/", data)
        print(response.content)

        self.assertEqual(response.status_code, 201)

    def test_canPostEventWithAllFields(self):
        org = Organization.objects.get(name="Setup Org")
        data = {
            "name": "Sunday Mass",
            "date": "2018-01-01",
            "organization": org.id
            }

        response = c.post("/events")

