from django.contrib.auth.models import User
from rest_framework import serializers
from api.models import Organization, Choir, UserProfile, Event, MusicRecord
from rest_framework.validators import UniqueValidator


class OrganizationSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source="owner.id")
    admins = serializers.PrimaryKeyRelatedField(many=True, required=False, queryset=User.objects.all())

    class Meta:
        model = Organization
        fields = ("id", "name", "address", "description", "created_date", "owner", "admins", "website_url")


class UserSerializer(serializers.ModelSerializer):
    owned_organizations = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    admin_of_organizations = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    #talents  = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    
    email = serializers.EmailField(required=True,validators=[UniqueValidator(queryset=User.objects.all())])
    username = serializers.CharField(validators=[UniqueValidator(queryset=User.objects.all())])
    password = serializers.CharField(min_length=8)
    first_name = serializers.CharField(min_length=2, max_length= 25)
    last_name = serializers.CharField(min_length=2, max_length= 25)
    class Meta:
        model = User
        fields = ('id', 'username','email', 'password', 'first_name', 'last_name', 'admin_of_organizations', 'owned_organizations')
    def create(self,validated_data):
        user = User.objects.create_user(validated_data['username'], 
            validated_data['email'],validated_data['password'],
            first_name=validated_data['first_name'], last_name=validated_data['last_name'])
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ('user','phone_number', 'address', 'bio', 'city', 'zip_code', 'state', 'date_of_birth') 
    def create(self, validated_data):
        user = self.context['request'].user
        user_profile = UserProfile.objects.create(user=user, date_of_birth = validated_data['date_of_birth'],
            phone_number=validated_data['phone_number'], address=validated_data['address'],
            bio=validated_data['bio'], city = validated_data['city'],
            zip_code = validated_data['zip_code'], state = validated_data['state'],)
        return user_profile
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

