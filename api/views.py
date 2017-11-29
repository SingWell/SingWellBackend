from api.models import Organization, Choir, Event
from django.contrib.auth.models import User
from api.serializers import OrganizationSerializer, UserSerializer, ChoirSerializer, EventSerializer
from rest_framework import generics


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