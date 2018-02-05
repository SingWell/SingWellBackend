from api.models import Organization, Choir, Event, MusicRecord, UserProfile
from django.contrib.auth.models import User
from api.serializers import OrganizationSerializer, UserSerializer, ChoirSerializer, UserProfileSerializer, EventSerializer, MusicRecordSerializer
from rest_framework import generics, status
from rest_framework.decorators import api_view
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from api.permissions import IsOwner,IsAdmin, IsChorister

class OrganizationList(generics.ListCreateAPIView):
    """List organizations or create a new organization"""
    def perform_create(self, serializer):
        if self.request.user.is_authenticated:
            serializer.save(owner=self.request.user)
        else:
            serializer.save(owner=User.objects.get(id=1))  # todo only allow people logged in to create an organization

    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer
    permission_classes= ()

class OrganizationDetail(generics.RetrieveUpdateDestroyAPIView):
    #permission_classes = (IsAdmin,IsOwner)
    permission_classes= ()
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer


class UserList(generics.ListAPIView):
    permission_classes= ()
    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserDetail(generics.RetrieveAPIView):
    permission_classes= ()
    queryset = User.objects.all()
    serializer_class = UserSerializer

class UserCreate(generics.GenericAPIView):
    serializer_class  = UserSerializer
    permission_classes=()
    def post(self, request):
        serializer =  UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            if user:
                token = Token.objects.create(user=user)
                user_profile = UserProfile.objects.create(user=user)
                json = serializer.data
                json['token']= token.key
                json.pop('password')
                return Response(json, status= status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
class UserEdit(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    queryset = UserProfile.objects.all()
    permission_classes=(IsOwner,)
    def update(self, request):
        if request.user.is_authenticated:
            user_profile = UserProfile.objects.get(user = request.user)
            serializer=  UserProfileSerializer(user_profile,data=request.data, partial=True, context={'request':request})
            if serializer.is_valid():
                user_profile = serializer.save()
                if user_profile:
                    return Response(serializer.data, status= status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
    
    def retrieve(self,request, pk=None):
        if request.user.is_authenticated:
            user_profile = UserProfile.objects.get(user = request.user)
            if user_profile :
                serializer = UserProfileSerializer(user_profile, context={'request':request}, partial=True)
                return_data = {'first_name' : request.user.first_name, 'last_name':request.user.last_name, 'email': request.user.email}
                return_data.update(serializer.data)
                return Response(return_data, status= status.HTTP_200_OK)
            return Response(status=status.HTTP_400_BAD_REQUEST)
        else :
            return Response(status=status.HTTP_401_UNAUTHORIZED)

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
    permission_classes= ()
    def get_queryset(self):
        queryset = Choir.objects.all()

        org_id = self.kwargs.get("org_id", None)  # default to none
        if org_id:
            queryset = queryset.filter(organization_id=org_id)

        return queryset


class ChoirDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ChoirSerializer
    permission_classes= ()

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