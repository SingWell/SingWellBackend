from rest_framework import permissions
from rest_framework.authtoken.models import Token
class IsOwner(permissions.BasePermission):
    def has_object_permission(self,request,view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user == obj.owner

class IsAdmin(permissions.BasePermission):
    def has_object_permission(self,request,view,obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user in obj.admins

class IsChorister(permissions.BasePermission):
    def has_object_permission(self,request,view,obj):
        if request.method in permissions.SAFE_METHODS and request.user in obj.choristers:
            return True
        return False