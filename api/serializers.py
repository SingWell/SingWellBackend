from django.contrib.auth.models import User
from rest_framework import serializers
from api.models import Organization, Choir, UserProfile, Event, MusicRecord, MusicResource, ProgramField, Announcement
from rest_framework.validators import UniqueValidator
from django.utils.translation import ugettext_lazy as _
from rest_framework.compat import authenticate
import datetime
from django.shortcuts import get_object_or_404


class OrganizationSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source="owner.id")
    admins = serializers.PrimaryKeyRelatedField(many=True, required=False, queryset=User.objects.all())

    def update(self, instance, validated_data):
        for field in validated_data:
            setattr(instance, field, validated_data.get(field, getattr(instance, field)))

        instance.save()

        return instance

    class Meta:
        model = Organization
        fields = ("id", "name", "address", "phone_number", "email", "description", "created_date", "owner", "admins", "website_url", "members")


class UserProfileSerializer(serializers.ModelSerializer):
    date_of_birth = serializers.DateField(format='%m-%d', input_formats=['%m-%d','%m-%d-%Y', '%m/%d', '%m/%d/%Y','%Y/%m/%d', '%Y-%m-%d'])
    age=serializers.SerializerMethodField(method_name='calculate_age')
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = UserProfile
        fields = ('user', 'phone_number', 'address', 'bio', 'city', 'zip_code', 'state', 'date_of_birth', 'age',
                  'profile_picture_link')

    def create(self, validated_data):
        user = validated_data.pop("user", None)
        user_profile = UserProfile.objects.create(user=user, **validated_data)
        return user_profile

    def calculate_age(self,instance):
        if instance.date_of_birth is not None:
            if datetime.datetime.now().year - instance.date_of_birth.year>116:
                return "Hidden"
            else:
                return instance.age


class UserSerializer(serializers.ModelSerializer):
    owned_organizations = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    admin_of_organizations = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    choirs = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    member_of_organizations = serializers.SerializerMethodField(method_name="get_organizations", read_only=True)
    organizations = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    email = serializers.EmailField(required=True, validators=[UniqueValidator(queryset=User.objects.all())])
    password = serializers.CharField(min_length=8, write_only=True)
    first_name = serializers.CharField(min_length=2, max_length=25, required=False)
    last_name = serializers.CharField(min_length=2, max_length=25, required=False)

    profile = UserProfileSerializer(required=False)

    class Meta:
        model = User
        fields = ('id', 'email', 'password', 'first_name', 'last_name', 'admin_of_organizations',
                  'owned_organizations', 'choirs', "member_of_organizations", "profile", "organizations")

    def get_organizations(self, user):
        organizations = user.organizations.all()
        orgs = []
        for org in organizations:
            orgs.append({'id':org.id,'name':org.name})

        return list(orgs)

    def create(self, validated_data):
        user = User.objects.create_user(validated_data.pop("email"), validated_data.pop("password"),
                                        first_name=validated_data.pop("first_name", ""),
                                        last_name=validated_data.pop("last_name", ""))
        user.save()
        if "profile" in validated_data and type(validated_data) == dict:
            validated_data["profile"]["user"] = user
        else:
            validated_data["profile"] = dict(user=user)
        user_profile = UserProfile.objects.create(**validated_data["profile"])
        user_profile.save()
        return user


    def update(self, user, validated_data):
        for key, value in validated_data.items():
            if key != "profile":
                setattr(user, key, value)
            else:
                for profile_key in validated_data["profile"]:
                    setattr(user.profile, profile_key, validated_data["profile"][profile_key])

        user.profile.save()
        user.save()

        return user


class ChoirSerializer(serializers.ModelSerializer):
    organization = serializers.PrimaryKeyRelatedField(many=False, queryset=Organization.objects.all())
    choristers = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    organization_name = serializers.StringRelatedField(many=False, read_only=True)
    director_name = serializers.SerializerMethodField()

    class Meta:
        model = Choir
        fields = ("id", "name", "meeting_day", "meeting_day_start_hour", "meeting_day_end_hour", "choristers",
                  "organization", "organization_name", "description", "director_name")

    def get_director_name(self, instance):
        """:type instance Choir"""
        return f"{instance.director.first_name} {instance.director.last_name}"


class ProgramFieldSerializer(serializers.ModelSerializer):
    event = serializers.PrimaryKeyRelatedField(many=False, queryset=Event.objects.all())
    music_record = serializers.PrimaryKeyRelatedField(many=False, queryset=MusicRecord.objects.all())
    title = serializers.CharField(source="music_record.title", read_only=True)
    composer = serializers.CharField(source="music_record.composer", read_only=True)

    class Meta:
        model = ProgramField
        fields = ("event", "music_record", "field_title", "order", "notes", "title", "composer", "id")


class EventSerializer(serializers.ModelSerializer):
    organization = serializers.PrimaryKeyRelatedField(many=False, queryset=Organization.objects.all())
    choirs = serializers.PrimaryKeyRelatedField(many=True, read_only=False, queryset=Choir.objects.all())
    program_music = ProgramFieldSerializer(many=True, source="programfield_set", read_only=True)

    class Meta:
        model = Event
        fields = ("id", "name", "date", "time", "location", "choirs", "organization", "program_music")


class MusicRecordSerializer(serializers.ModelSerializer):
    organization = serializers.PrimaryKeyRelatedField(many=False, queryset=Organization.objects.all())
    events = EventSerializer(read_only=True, source="events")

    class Meta:
        model = MusicRecord
        fields = ("id", "title", "composer", "arranger", "publisher", "instrumentation", "organization", "source", "program_info")

    # def get_program_info(self, instance):
    #     """:type instance MusicRecord"""
    #     return str(instance.events.all().order_by("date"))



class MusicResourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = MusicResource
        fields = ("id", "title", "music_record", "description")

class AnnouncementSerializer(serializers.ModelSerializer):
    choir = serializers.PrimaryKeyRelatedField(many=False, queryset=Choir.objects.all())
    creator = serializers.PrimaryKeyRelatedField(many=False, queryset=User.objects.all())
    
    class Meta:
        model = Announcement
        fields = ("id", "title", "choir", "message", "creator")

# overriding default AuthTokenSerializer in Django Rest Auth Token extension
class AuthTokenSerializer(serializers.Serializer):
    email = serializers.CharField(label=_("Email"))
    password = serializers.CharField(
        label=_("Password"),
        style={'input_type': 'password'},
        trim_whitespace=False
        )

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        username = get_object_or_404(User, email=email)
        if email and password:
            user = authenticate(request=self.context.get('request'),
                                username=username, password=password)

            # The authenticate call simply returns None for is_active=False
            # users. (Assuming the default ModelBackend authentication
            # backend.)
            if not user:
                msg = _('Unable to log in with provided credentials.')
                raise serializers.ValidationError(msg, code='authorization')
        else:
            msg = _('Must include "email" and "password".')
            raise serializers.ValidationError(msg, code='authorization')

        attrs['user'] = user
        return attrs
