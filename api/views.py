from api.models import Organization, Choir, Event, MusicRecord, UserProfile, MusicResource, FileResource,TextResource
from django.contrib.auth.models import User
from api.serializers import OrganizationSerializer, UserSerializer, ChoirSerializer, UserProfileSerializer, EventSerializer, MusicRecordSerializer, AuthTokenSerializer, MusicResourceSerializer
from rest_framework import generics, status,parsers, renderers
from rest_framework.decorators import api_view, permission_classes
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from api.permissions import IsOwner,IsAdmin, IsChorister
from rest_framework.permissions import AllowAny
from rest_framework.schemas import  ManualSchema
from rest_framework.views import APIView
from django.http import HttpResponse
from django.conf import settings
import boto3
import mimetypes
import io
import coreapi
import coreschema
import base64
from api.parse_library import parse_library

def _filter_queryset_(queryset, params):
    pass


class OrganizationList(generics.ListCreateAPIView):
    """List organizations or create a new organization"""
    def perform_create(self, serializer):
        if self.request.user.is_authenticated:
            serializer.save(owner=self.request.user)
        else:
            serializer.save(owner=User.objects.all()[0])  # todo only allow people logged in to create an organization

    # def update(self):

    permission_classes = ()
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer

class OrganizationDetail(generics.RetrieveUpdateDestroyAPIView):
    #permission_classes = (IsAdmin,IsOwner)
    permission_classes= ()
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer

class UserList(generics.ListCreateAPIView):
    permission_classes= ()
    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserDetail(generics.RetrieveUpdateAPIView):
    permission_classes= ()
    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserCreate(generics.GenericAPIView):
    serializer_class  = UserSerializer
    permission_classes=()
    def post(self, request):
        request.data['username']=request.data['email']
        serializer =  UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            if user:
                token = Token.objects.create(user=user)
                user.save()
                json = serializer.data
                json['token']= token.key
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

class UserLogin(APIView):
    serializer_class = AuthTokenSerializer
    throttle_classes = ()
    permission_classes = ()
    parser_classes = (parsers.FormParser, parsers.MultiPartParser, parsers.JSONParser,)
    renderer_classes = (renderers.JSONRenderer,)

    schema = ManualSchema(
        fields=[
            coreapi.Field(
                name="email",
                required=True,
                location='form',
                schema=coreschema.String(
                    title="Email",
                    description="Valid email for authentication",
                ),
            ),
            coreapi.Field(
                name="password",
                required=True,
                location='form',
                schema=coreschema.String(
                    title="Password",
                    description="Valid password for authentication",
                ),
            ),
        ],
    )



    def post(self,request, *args,**kwargs):
        serializer = self.serializer_class(data=request.data, context= {'request':request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        user_id =user.id
        token, created = Token.objects.get_or_create(user=user)
        return Response({'token': token.key,'user_id':user_id})

class ChoirList(generics.ListCreateAPIView):
    serializer_class = ChoirSerializer
    permission_classes= ()

    def get_queryset(self):
        queryset = Choir.objects.all()

        org_id = self.request.query_params.get("organization", None)  # default to none
        if org_id:
            queryset = queryset.filter(organization_id=org_id)
        user_id = self.request.query_params.get("user", None)
        if user_id:
            queryset = queryset.filter(choristers__pk=user_id)

        # Todo: refactor this into a general function

        return queryset


class ChoirDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ChoirSerializer
    permission_classes= ()
    queryset = Choir.objects.all()

@api_view(["GET", "POST"])
@permission_classes((AllowAny,))
def ChoirRoster(request, choir_id):
    # TODO: Figure out how to do this in a rest framework way
    """Retrieve the roster for a choir or add a user to a choir."""
    if request.method == "GET":
        choir = Choir.objects.get(id=choir_id)
        roster = choir.choristers
        serializer = UserSerializer(roster, many=True)
        return Response(serializer.data)
    else:
        if request.method == "POST":
            user_id = request.POST["user_id"]
            choir = Choir.objects.get(id=choir_id)
            user = User.objects.get(id=user_id)
            choir.choristers.add(user)
            choir.save()

            serializer = ChoirSerializer(choir)

            return Response(serializer.data)


@api_view(["GET"])
def ChoirsForUser(request, user_id):
    user = User.objects.get(id=user_id)
    choirs = user.choir_set
    serializer = ChoirSerializer(choirs, many=True)
    return Response(serializer.data)


class EventList(generics.ListCreateAPIView):
    serializer_class = EventSerializer
    permission_classes=()

    def get_queryset(self):
        queryset = Event.objects.all()

        organization_id = self.request.query_params.get('organization', None)
        if organization_id is not None:
            organization = Organization.objects.get(id=organization_id)
            queryset = queryset.filter(organization=organization)

        return queryset


class EventDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = EventSerializer
    permission_classes = ()
    queryset = Event.objects.all()


class MusicRecordList(generics.ListCreateAPIView):
    serializer_class = MusicRecordSerializer
    permission_classes=()
    def get_queryset(self):
        queryset = MusicRecord.objects.all()
        org_id = self.request.query_params.get("organization", None)  # default to none
        if org_id:
            organization = Organization.objects.get(id=org_id)
            queryset = queryset.filter(organization=organization)
        return queryset


class MusicRecordDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = MusicRecordSerializer
    permission_classes = ()
    queryset = MusicRecord.objects.all()
    def retrieve(self,request,pk):
        try:
            music_record = MusicRecord.objects.get(id=pk)
        except:
            return Response(status=404)
        serializer = self.serializer_class(music_record)
        # serializer.is_valid(raise_exception=True)
        json = serializer.data
        json['music_resources'] = [{'resource_id':resource.id, 'type':resource.type, 'extension':(resource.fileresource.file_type if resource.type=='file' else 'NOT_APPLICABLE')} for resource in MusicResource.objects.filter(music_record_id=pk)]
        return Response(json, status= 200) 



class MusicResourceList(generics.ListCreateAPIView):
    serializer_class = MusicResourceSerializer
    permission_classes = ()

    def get_queryset(self):
        queryset = MusicResource.objects.all()
        org_id = self.request.query_params.get("organization", None)  # default to none
        if org_id:
            organization = Organization.objects.get(id=org_id)
            queryset = queryset.filter(organization=organization)
        return queryset


class MusicResourceDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = MusicResourceSerializer
    permission_classes = ()
    queryset = MusicResource.objects.all()


#TODO : Do this in a DRest way
@api_view(["GET", "POST"])
@permission_classes((AllowAny,))
def MusicResourceUpDown(request):
    if request.method=='POST':
        
        aws_a_k_i = getattr(settings, "AWS_ACCESS_KEY_ID")
        aws_s_a_k = getattr(settings, "AWS_SECRET_KEY")
        s3 = boto3.client('s3',
                          aws_access_key_id=aws_a_k_i,
                          aws_secret_access_key=aws_s_a_k,)
        if request.POST['type'] == 'file':
            for key in request.FILES:
                filedata= request.FILES[key]
                record_id = request.POST['record_id']
                filename = '{0}/{1}'.format(record_id,key)
                s3.upload_fileobj(filedata, 'singwell', filename)
                object_url = "https://s3.amazonaws.com/singwell/{}".format(filename)
                try: 
                    file_resource = FileResource.objects.create(file_name=filename, file_type=key.split('.')[-1],title=key, music_record_id= record_id, type='file')
                    file_resource.save()
                except Exception as e: 
                    print(e)
                    return HttpResponse(status= 400)
                return HttpResponse(status= 201)
        else: 
            return HttpResponse(status=404)
        # else:
        #     text_resource=FileResource.objects.get_or_create(title=)
    if request.method=='GET':
        aws_a_k_i = getattr(settings, "AWS_ACCESS_KEY_ID")
        aws_s_a_k = getattr(settings, "AWS_SECRET_KEY")

        s3 = boto3.client('s3',
                          aws_access_key_id=aws_a_k_i,
                          aws_secret_access_key=aws_s_a_k,)
        
        resource_id = request.query_params.get('resource_id',None)
        record_id = request.query_params.get('record_id',None)
        try: 
            resource = MusicResource.objects.get(id=resource_id, music_record_id = record_id)
        except Exception as e:
            print(e)
            return HttpResponse("File with id #{} does not exist associated with this record id".format(resource_id), status=404)
        if resource.type == 'file' :
            file_key = '{0}/{1}'.format(record_id,resource.title)
            filedata = io.BytesIO(b"")  # create an in memory file-like to download from S3 to
            s3.download_fileobj(Bucket="singwell", Key=file_key, Fileobj=filedata)  # download file from S3
            filedata.seek(0)  # the IO object has its file pointer pointing to the end of the file, so move it
            response = HttpResponse(base64.b64encode(filedata.getvalue()), status=200)
            response["Content-Type"] = resource.fileresource.file_type
            
            response["Content-Disposition"] = 'inline; filename="{}"'.format(resource.title)

            return response



@api_view(["POST"])
@permission_classes((AllowAny,))
def LibraryUpload(request):
    if request.method=="POST":
        for key in request.FILES:
            filedata= request.FILES[key]
            organization_id = request.POST['organization_id']
            if (parse_library(filedata, organization_id)) ==True:
                return HttpResponse(status=201)
            else :
                return HttpResponse(status=400)

# @api_view(["POST"])
# @permission_classes((AllowAny,))
# def ProfilePictureUpload(request):
#     if request.method=='POST':
#         aws_a_k_i = getattr(settings, "AWS_ACCESS_KEY_ID")
#         aws_s_a_k = getattr(settings, "AWS_SECRET_KEY")
#         s3 = boto3.client('s3',
#                         aws_access_key_id=aws_a_k_i,
#                         aws_secret_access_key=aws_s_a_k,)
#         for key in request.FILES:
#             filedata=request.FILES[key]
            
#             user_id = request.POST['user_id']
#             try: 
#                 user_profile = UserProfile.objects.get(user_id=user_id)
#                 user_profile.profile_picture_link = "https://s3.amazonaws.com/singwell/{}".format(filename) 
#             except:
#                 return HttpResponse(status=404)
#             filename = '{0}/{1}'.format(user_id,key)
#             s3.upload_fileobj(filedata, 'singwell', filename)
#             object_url = "https://s3.amazonaws.com/singwell/{}".format(filename)
#             return HttpResponse(status=201)
    