from django.test import TestCase
from rest_framework.test import APIClient as Client
from api.models import *
from api.serializers import *
import json

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

    def test_onlyUsernameAndPasswordAreRequiredToCreateUser(self):
        response = c.post("/users/", {"username": "jake@smu.edu", "password": "password"})
        print(response.content)
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
            "name" : "Setup Org for Events",
            "owner": User.objects.get(email="joien@smu.edu")
            }

        OrganizationSerializer().create(validated_data=org_data)

    def test_canPostEventWithRequiredFields(self):
        org = Organization.objects.get(name="Setup Org for Events")
        data = {
            "name": "Sunday Mass",
            "date": "2018-01-01",
            "organization": org.id
            }

        response = c.post(f"/events/", data)

        self.assertEqual(response.status_code, 201)

    def test_canPostEventWithAllFields(self):
        org = Organization.objects.get(name="Setup Org for Events")
        data = {
            "name": "Sunday Mass",
            "date": "2018-01-01",
            "organization": org.id
            }

        response = c.post("/events")


class MusicRecordTestCase(TestCase):
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
            "name" : "Setup Org for Music Records",
            "owner": User.objects.get(email="joien@smu.edu")
            }

        OrganizationSerializer().create(validated_data=org_data)

        musicRecordData = {
                "title": "A test record",
                "composer": "Mozart",
                "arranger": "Mike Tomaro",
                "publisher": "Pender's",
                "instrumentation": "SATB",
                "organization": Organization.objects.get(name="Setup Org for Music Records")
            }

        MusicRecordSerializer().create(validated_data=musicRecordData)

    def test_canPostMusicRecord(self):
        data = {
            "title": "Another test record",
            "composer": "Bach",
            "arranger": "Jimjam Flimflam",
            "publisher": "Hah",
            "instrumentation": "SSTB",
            "organization": Organization.objects.get(name="Setup Org for Music Records").id
            }

        oldCount = MusicRecord.objects.count()
        response = c.post("/musicRecords/", data)
        newCount = MusicRecord.objects.count()

        self.assertEqual(response.status_code, 201)
        self.assertEqual(newCount, oldCount + 1, "Record count after POST should be one greater than before")

    def test_canPatchMusicRecord(self):
        data = {
            "publisher": "Pender's"
            }

        oldCount = MusicRecord.objects.count()
        response = c.patch(f"/musicRecords/{MusicRecord.objects.get(title='A test record').id}/", data)
        newCount = MusicRecord.objects.count()

        self.assertIn(response.status_code, [200, 201, 204])
        self.assertEqual(oldCount, newCount)