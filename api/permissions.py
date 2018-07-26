from rest_framework import permissions

class IsMatchOwner(permissions.BasePermission):
    """
    User that is currently logged in has to be owner of this match
    """

    def has_object_permission(self, request, view, obj):
        return request.user == obj.user