from rest_framework import permissions
from django.utils.translation import gettext_lazy as _


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    Others can only view.
    """
    message = _("You must be the owner of this object to perform this action.")

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed for any request (GET, HEAD, OPTIONS)
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions are only allowed to the owner
        return obj.user == request.user


class IsStreamOwner(permissions.BasePermission):
    """
    Custom permission to only allow stream owners to perform certain actions.
    """
    message = _("You must be the stream owner to perform this action.")

    def has_permission(self, request, view):
        # Allow all GET requests
        if request.method in permissions.SAFE_METHODS:
            return True
            
        # Check if stream_id is in the URL parameters
        stream_id = view.kwargs.get('stream_id')
        if not stream_id:
            return False
            
        # Check if user owns the stream
        return request.user.streams.filter(id=stream_id).exists()


class IsNotBanned(permissions.BasePermission):
    """
    Custom permission to prevent banned users from performing certain actions.
    """
    message = _("You are currently banned from performing this action.")

    def has_permission(self, request, view):
        return not hasattr(request.user, 'ban') or not request.user.ban.is_active 