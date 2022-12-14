from rest_framework import permissions


class IsAuthorOrReadOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        return (
            request.method in ('GET', 'RETRIEVE')
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        return (
            request.method == 'GET'
            or obj.author == request.user
        )
