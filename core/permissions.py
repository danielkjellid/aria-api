from django.contrib.auth.models import Group, Permission
from rest_framework.permissions import BasePermission


class HasUserOrGroupPermission(BasePermission):
    """
    Checks if the user is assigned needed permission to perform action by checking if 
    the required permissions are contained in a union of the two sets of permissions
    """

    def has_permission(self, request, view):

        if request.user.is_superuser:
            return True

        user_permissions = set(Permission.objects.filter(user=request.user).values_list('codename', flat=True))
        group_permissions = set(Permission.objects.filter(group__user=request.user).values_list('codename', flat=True))

        # get required permissions variable from view
        required_permissions_mapping = getattr(view, 'required_permissions', {})
        # determine if the required permissions for the particular request method
        required_permissions = set(required_permissions_mapping.get(request.method, []))

        if required_permissions.issubset(user_permissions | group_permissions):
            return True