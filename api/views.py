from api.models import Organization, Choir, UserProfile
from django.contrib.auth.models import User
from api.serializers import OrganizationSerializer, UserSerializer, ChoirSerializer, UserProfileSerializer
from rest_framework import generics, status
from api.permissions import IsOwner,IsAdmin, IsChorister
from rest_framework.response import Response
from rest_framework.authtoken.models import Token

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
    permission_classes = (IsAdmin,IsOwner)
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer


class UserList(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserDetail(generics.RetrieveAPIView):
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
                return Response(serializer.data, status= status.HTTP_200_OK)
            return Response(status=status.HTTP_400_BAD_REQUEST)
        else :
            return Response(status=status.HTTP_401_UNAUTHORIZED)

class ChoirList(generics.ListAPIView):
    serializer_class = ChoirSerializer

    def get_queryset(self):
        queryset = Choir.objects.all()

        org_id = self.kwargs.get("org_id", None)  # default to none
        if org_id:
            queryset = queryset.filter(organization_id=org_id)

        return queryset



class ChoirDetail(generics.RetrieveAPIView):
    serializer_class = ChoirSerializer

    def get_queryset(self):
        queryset = Choir.objects.all()

        org_id = self.kwargs.get("org_id", None)  # default to none
        if org_id:
            queryset = queryset.filter(organization_id=org_id)

        return queryset