from rest_framework import permissions


class IsAuthorOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        if request.method in ['POST', 'PATCH', 'DELETE']:
            return request.user.is_authenticated
        if request.user.is_authenticated:
            allowed = (
                obj.author == request.user,
                request.user.is_admin,
            )
            return any(allowed)
        return False
