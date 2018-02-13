from django.contrib.auth.models import User
from rest_framework import serializers
from api.models import Organization, Choir, UserProfile, Event, MusicRecord
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

        return instance

    class Meta:
        model = Organization
        fields = ("id", "name", "address", "phone_number", "email", "description", "created_date", "owner", "admins", "website_url")


class UserSerializer(serializers.ModelSerializer):
    owned_organizations = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    admin_of_organizations = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    choirs = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    member_of_organizations = serializers.SerializerMethodField(method_name="get_organizations", read_only=True)

    email = serializers.EmailField(required=False,validators=[UniqueValidator(queryset=User.objects.all())])
    username = serializers.CharField(validators=[UniqueValidator(queryset=User.objects.all())], required=True)
    password = serializers.CharField(min_length=8, write_only=True)
    first_name = serializers.CharField(min_length=2, max_length= 25, required=False)
    last_name = serializers.CharField(min_length=2, max_length= 25, required=False)


    class Meta:
        model = User
        fields = ('id', 'username','email', 'password', 'first_name', 'last_name', 'admin_of_organizations', 'owned_organizations', 'choirs', "member_of_organizations")


    def get_organizations(self, user):
        choirs = user.choirs.all()
        orgs = set()
        for choir in choirs:
            orgs.add(choir.organization_id)

        return list(orgs)

    def create(self,validated_data):
        user = User.objects.create_user(validated_data.get("username"),
            validated_data.get("email"),validated_data.get("password"),
            first_name=validated_data.get("first_name", ""), last_name=validated_data.get("last_name", ""))
        return user

class UserProfileSerializer(serializers.ModelSerializer):
    date_of_birth = serializers.DateField(format='%m-%d', input_formats=['%m-%d','%m-%d-%Y'])
    age=serializers.SerializerMethodField(method_name='calculate_age')
    class Meta:
        model = UserProfile
        fields = ('user','phone_number', 'address', 'bio', 'city', 'zip_code', 'state', 'date_of_birth', 'age') 
    def create(self, validated_data):
        user = self.context['request'].user
        user_profile = UserProfile.objects.create(user=user, date_of_birth = validated_data.get("date_of_birth", None),
            phone_number=validated_data.get("phone_number", None), address=validated_data.get("address", None),
            bio=validated_data.get("bio", None), city = validated_data("city", None),
            zip_code = validated_data.get("zip_code", None), state = validated_data.get("state", None),)
        return user_profile
    def calculate_age(self,instance):
        if instance.date_of_birth is not None:
            if datetime.datetime.now().year - instance.date_of_birth.year>116:
                return "Hidden"
            else:
                return instance.age
    # def update(self,validated_data):
    #     user = self.context['request'].user
    #     user_profile = UserProfile.objects.create(user=user, date_of_birth = validated_data['date_of_birth'],
    #         phone_number=validated_data['phone_number'], address=validated_data['address'],
    #         bio=validated_data['bio'], city = validated_data['city'],
    #         zip_code = validated_data['zip_code'], state = validated_data['state'],)
    #     return user_profile
class ChoirSerializer(serializers.ModelSerializer):
    organization = serializers.PrimaryKeyRelatedField(many=False, queryset=Organization.objects.all())
    choristers = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    organization_name = serializers.StringRelatedField(many=False, read_only=True)


    class Meta:
        model = Choir
        fields = ("id", "name", "meeting_day", "meeting_day_start_hour", "meeting_day_end_hour", "choristers",
                  "organization", "organization_name", "description")


class EventSerializer(serializers.ModelSerializer):
    organization = serializers.PrimaryKeyRelatedField(many=False, queryset=Organization.objects.all())
    choirs = serializers.PrimaryKeyRelatedField(many=True, read_only=False, queryset=Choir.objects.all())

    class Meta:
        model = Event
        fields = ("id", "name", "date", "time", "location", "choirs", "organization")


class MusicRecordSerializer(serializers.ModelSerializer):
    organization = serializers.PrimaryKeyRelatedField(many=False, queryset=Organization.objects.all())

    class Meta:
        model = MusicRecord
        fields = ("id", "title", "composer", "arranger", "publisher", "instrumentation", "organization")

#overriding default AuthTokenSerializer in Django Rest Auth Token extension
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
        username = get_object_or_404(User,email=email)
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