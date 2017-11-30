from api.models import Organization, Choir, Event, MusicRecord
from django.contrib.auth.models import User
from api.serializers import OrganizationSerializer, UserSerializer, ChoirSerializer, EventSerializer, MusicRecordSerializer
from rest_framework import generics
from rest_framework.decorators import api_view

from rest_framework.response import Response



class OrganizationList(generics.ListCreateAPIView):
    """List organizations or create a new organization"""
    def perform_create(self, serializer):
        if self.request.user.is_authenticated:
            serializer.save(owner=self.request.user)
        else:
            serializer.save(owner=User.objects.get(id=1))  # todo only allow people logged in to create an organization

    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer


class OrganizationDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer


class UserList(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserDetail(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


@api_view(["GET", "POST"])
def ChoirRoster(request, org_id, choir_id):
    # TODO: Figure out how to do this in a rest framework way
    """Retrieve the roster for a choir or add a user to a choir."""
    if request.method == "GET":
        choir = Choir.objects.filter(organization_id=org_id).get(id=choir_id)
        roster = choir.choristers
        serializer = UserSerializer(roster, many=True)
        return Response(serializer.data)
    else:
        if request.method == "POST":
            user_id = request.POST["user_id"]
            choir = Choir.objects.filter(organization_id=org_id).get(id=choir_id)
            user = User.objects.get(user_id=user_id)
            choir.choristers.add(user)
            choir.save()

            serializer = ChoirSerializer(choir)

            return Response(serializer.data)


class ChoirList(generics.ListCreateAPIView):
    serializer_class = ChoirSerializer

    def get_queryset(self):
        queryset = Choir.objects.all()

        org_id = self.kwargs.get("org_id", None)  # default to none
        if org_id:
            queryset = queryset.filter(organization_id=org_id)

        return queryset


class ChoirDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ChoirSerializer

    def get_queryset(self):
        queryset = Choir.objects.all()

        org_id = self.kwargs.get("org_id", None)  # default to none
        if org_id:
            queryset = queryset.filter(organization_id=org_id)

        return queryset


@api_view(["GET"])
def ChoirsForUser(request, user_id):
    user = User.objects.get(id=user_id)
    choirs = user.choir_set
    serializer = ChoirSerializer(choirs, many=True)
    return Response(serializer.data)



class EventList(generics.ListCreateAPIView):
    serializer_class = EventSerializer

    def get_queryset(self):
        queryset = Event.objects.all()

        org_id = self.kwargs.get("org_id", None)  # default to none
        if org_id:
            queryset = queryset.filter(organization_id=org_id)

        return queryset


class EventDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = EventSerializer

    def get_queryset(self):
        queryset = Event.objects.all()

        org_id = self.kwargs.get("org_id", None)  # default to none
        if org_id:
            queryset = queryset.filter(organization_id=org_id)

        return queryset


class MusicRecordList(generics.ListCreateAPIView):
    serializer_class = MusicRecordSerializer

    def get_queryset(self):
        queryset = MusicRecord.objects.all()

        org_id = self.kwargs.get("org_id", None)  # default to none
        if org_id:
            queryset = queryset.filter(organization_id=org_id)

        return queryset


class MusicRecordDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = MusicRecordSerializer

    def get_queryset(self):
        queryset = MusicRecord.objects.all()

        org_id = self.kwargs.get("org_id", None)  # default to none
        if org_id:
            queryset = queryset.filter(organization_id=org_id)

        return queryset