from rest_framework import serializers
from api.models import Organization


# class OrganizationSerializer(serializers.Serializer):
#     id = serializers.IntegerField(read_only=True)
#     name = serializers.CharField(max_length=50, required=True, allow_blank=False, allow_null=False)
#     address = serializers.CharField(max_length=50, allow_blank=False, allow_null=False, required=True)
#     contact_phone_number = serializers.CharField(max_length=20, allow_null=True, allow_blank=True, required=False)
#     contact_email = serializers.CharField(max_length=350, allow_null=False, allow_blank=False, required=True)
#     description = serializers.CharField()
#     created_date = serializers.DateTimeField()
#
#     def create(self, validated_data):
#         """
#         Create and return a new `Snippet` instance, given the validated data.
#         """
#         return Organization.objects.create(**validated_data)
#
#     def update(self, instance, validated_data):
#         """
#         Update and return an existing `Organization` instance, given the validated data.
#         """
#
#         instance.name = validated_data.get('name', instance.name)
#         instance.address = validated_data.get('address', instance.address)
#         instance.contact_phone_number = validated_data.get('contact_phone_number', instance.contact_phone_number)
#         instance.contact_email = validated_data.get('contact_email', instance.contact_email)
#         instance.description = validated_data.get('description', instance.description)
#         instance.created_date = validated_data.get('created_date', instance.created_date)
#         instance.save()
#         return instance

class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ("id", "name", "address", "contact_phone_number", "contact_email", "description", "created_date")
