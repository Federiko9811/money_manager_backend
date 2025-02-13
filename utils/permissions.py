from rest_framework import permissions


class IsOwner(permissions.BasePermission):
    """
    Custom permission to allow only the owner of an object to access it.
    """

    def has_object_permission(self, request, view, obj):
        # Ensure the authenticated user is the owner of the object
        return obj.user == request.user

    def has_permission(self, request, view):
        # Allow any user to create new objects (e.g., POST requests)
        if request.method == 'POST':
            return True
        # For other methods (GET, PUT, DELETE), check if the user is authenticated
        return request.user and request.user.is_authenticated
