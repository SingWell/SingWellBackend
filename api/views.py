from api.models import Organization, Choir, Event, MusicRecord, UserProfile, MusicResource, FileResource, TextResource, \
    ProgramField
from django.contrib.auth.models import User
from api.serializers import OrganizationSerializer, UserSerializer, ChoirSerializer, UserProfileSerializer, \
    EventSerializer, MusicRecordSerializer, AuthTokenSerializer, MusicResourceSerializer, ProgramFieldSerializer
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
from copy import deepcopy
import json
import base64
from api.parse_library import parse_library


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
                return Response(json, status=status.HTTP_201_CREATED)
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
def ChoirRoster(request, pk):
    # TODO: Figure out how to do this in a rest framework way
    """Retrieve the roster for a choir or add a user to a choir."""
    try:
        choir = Choir.objects.get(id=pk)
    except Choir.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == "GET":
        roster = choir.choristers
        serializer = UserSerializer(roster, many=True)
        return Response(serializer.data)
    else:
        if request.method == "POST":
            user_id = request.data.get("user_id", None)
            choir = Choir.objects.get(id=pk)
            user = User.objects.get(id=user_id)
            choir.choristers.add(user)
            choir.save()

            serializer = ChoirSerializer(choir)

            return Response(serializer.data)


@api_view(["GET"])
@permission_classes((AllowAny,))
def EventsForChoir(request, pk):
    try:
        choir = Choir.objects.get(pk=pk)
    except Choir.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    return Response(EventSerializer(choir.events, many=True).data)


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


class EventProgramList(APIView):
    permission_classes = ()

    def get(self, request, pk):
        try:
            event = Event.objects.get(pk=pk)
            ser = EventSerializer(event)
            programs = [program_field for program_field in ser.data["program_music"]]
            return Response(programs, status=status.HTTP_200_OK)
        except Event.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)


    def post(self, request, pk):
        data = deepcopy(request.data)

        # return Response(data, status=status.HTTP_201_CREATED)
        if type(request.data) == list:
            for program_field in data:
                program_field["event"] = pk
        else:
            data["event"] = pk

        pf_ser = ProgramFieldSerializer(many=type(data)==list, data=data)
        if pf_ser.is_valid():
            pf_ser.save()
            return Response(pf_ser.data, status=status.HTTP_201_CREATED)
        else:
            return Response(pf_ser.errors, status=status.HTTP_400_BAD_REQUEST)


class ProgramFieldDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ProgramFieldSerializer
    permission_classes = ()
    queryset = ProgramField.objects.all()


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
        json['music_resources'] = [{'url':(resource.textresource.field if resource.type=='youtube_link' else 'NOT APPLICABLE'), 'description':resource.description, 'resource_id':resource.id, 'title':resource.title, 'type':resource.type, 'extension':(resource.fileresource.file_type if resource.type=='file' else 'NOT_APPLICABLE')} for resource in MusicResource.objects.filter(music_record_id=pk)]
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
        if 'type' not in request.POST or 'record_id' not in request.POST:
            return HttpResponse('Type or record id not specified in request', status=403)
        record_id = request.POST['record_id']
        description = None
        if 'description' in request.POST:
            description = request.POST['description']
        if request.POST['type'] == 'file':
            for key in request.FILES:
                filedata= request.FILES[key]
                filename = '{0}/{1}'.format(record_id,key)
                s3.upload_fileobj(filedata, 'singwell', filename)
                object_url = "https://s3.amazonaws.com/singwell/{}".format(filename)
                try: 
                    file_resource, created = FileResource.objects.get_or_create(file_name=filename, file_type=key.split('.')[-1],title=key, music_record_id= record_id, type='file', description = description)
                    file_resource.save()
                    if created==False:
                        return HttpResponse("File already exists", status=200)
                except Exception as e: 
                    print(e)
                    return HttpResponse(status= 400)
                return HttpResponse(status= 201)
        elif request.POST['type'] == 'youtube_link':
            url = request.POST['url']
            title = request.POST['title']
            try:
                text_resource, created = TextResource.objects.get_or_create(title = title, music_record_id = record_id, type='youtube_link', field=url, description=description)
                if created==False:
                    return HttpResponse("Link already exists", status=200)
                text_resource.save()
            except Exception as e:
                return HttpResponse(e, status=400)
            return HttpResponse(status=201)
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
            return HttpResponse("Resource with id #{} does not exist associated with this record id".format(resource_id), status=404)
        if resource.type == 'file' :
            file_key = '{0}/{1}'.format(record_id,resource.title)
            filedata = io.BytesIO(b"")  # create an in memory file-like to download from S3 to
            s3.download_fileobj(Bucket="singwell", Key=file_key, Fileobj=filedata)  # download file from S3
            filedata.seek(0)  # the IO object has its file pointer pointing to the end of the file, so move it
            response = HttpResponse(base64.b64encode(filedata.getvalue()), status=200)
            response["Content-Type"] = resource.fileresource.file_type
            
            response["Content-Disposition"] = 'inline; filename="{}"'.format(resource.title)

            return response
        if resource.type=='youtube_link':
            return Response({'url':resource.textresource.field, 'title':resource.title, 'type':resource.type, 'description':resource.description}, status=200)



@api_view(["POST"])
@permission_classes((AllowAny,))
def LibraryUpload(request):
    if request.method=="POST":
        if 'organization_id' not in request.POST:
            return HttpResponse('Not specified organization id in request', status=403)
        for key in request.FILES:
            filedata= request.FILES[key]
            organization_id = request.POST['organization_id']
            if (parse_library(filedata, organization_id)) ==True:
                return HttpResponse(status=201)
            else :
                return HttpResponse(status=400)

@api_view(["GET", "POST"])
@permission_classes((AllowAny,))
def PictureUpDown(request):
    if request.method=='POST':
        if ('picture_type' not in request.POST or 'id' not in request.POST or request.POST['picture_type'] not in ['organization', 'choir', 'profile']):
            return HttpResponse('Invalid request', status=403)
        
        aws_a_k_i = getattr(settings, "AWS_ACCESS_KEY_ID")
        aws_s_a_k = getattr(settings, "AWS_SECRET_KEY")
        s3 = boto3.client('s3',
                        aws_access_key_id=aws_a_k_i,
                        aws_secret_access_key=aws_s_a_k,)
        for key in request.FILES:
            filedata=request.FILES[key]
            id = request.POST['id']
            picture_type = request.POST['picture_type']
            filename = '{0}/{1}/{2}'.format(picture_type,id,key)
            if picture_type=='profile':
                try: 
                    user_profile = UserProfile.objects.get(user_id=id)
                    user_profile.profile_picture_link = filename 
                    user_profile.save()
                except:
                    return HttpResponse(status=404)
            elif picture_type=='organization':
                try:
                    org = Organization.objects.get(id=id)
                    org.avatar_link = filename
                    org.save()
                except:
                    return HttpResponse(status=404)
            elif picture_type=='choir':
                try:
                    choir = Choir.objects.get(id=id)
                    choir.avatar_link = filename
                    choir.save()
                except:
                    return HttpResponse(status=404)
            s3.upload_fileobj(filedata, 'singwell', filename)
            return HttpResponse(status=201)
    elif request.method=='GET':
        aws_a_k_i = getattr(settings, "AWS_ACCESS_KEY_ID")
        aws_s_a_k = getattr(settings, "AWS_SECRET_KEY")
        s3 = boto3.client('s3',
                        aws_access_key_id=aws_a_k_i,
                        aws_secret_access_key=aws_s_a_k,)
        id = request.query_params.get('id',None)
        picture_type = request.query_params.get('picture_type', None)
        link = None
        if picture_type=='profile':       
            try: 
                user_profile = UserProfile.objects.get(user_id=id)
                link = user_profile.profile_picture_link
            except Exception as e:
                print(e)
                return HttpResponse("User does not exist", status=404)
        elif picture_type =='organization':
            try:
                organization = Organization.objects.get(id=id)
                link = organization.avatar_link
            except Exception as e:
                print(e)
                return HttpResponse("Organization does not exist", status=404)
        elif picture_type =='choir':
            try:
                choir = Choir.objects.get(id=id)
                link = choir.avatar_link
            except Exception as e:
                print(e)
                return HttpResponse("Choir does not exist", status=404)
                
        if link is not None :
            filedata = io.BytesIO(b"")  # create an in memory file-like to download from S3 to
            s3.download_fileobj(Bucket="singwell", Key=link, Fileobj=filedata)  # download file from S3
            filedata.seek(0)  # the IO object has its file pointer pointing to the end of the file, so move it
            response = HttpResponse(base64.b64encode(filedata.getvalue()), status=200)
            response["Content-Type"] = link.split('.')[:-1]
            
            response["Content-Disposition"] = 'inline; filename="{}"'.format(link)

            return response
        else:
            return HttpResponse("Picture not available for " + picture_type + "With id "+ str(id), status=404)