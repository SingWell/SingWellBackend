from django.test import TestCase, Client
from api.models import *
from api.serializers import *

c = Client()

# Create your tests here.
class TestTestCase(TestCase):
    def setUp(self):
        pass

    def testCaseCanRun(self):
        self.assertEqual("ab", "ab")


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

    def canPostOrganization(self):
        response = c.post("")



    def canPostEvent(self):
        response = c.post("organizations")