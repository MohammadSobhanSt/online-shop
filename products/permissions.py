from rest_framework import permissions


class IsSeller(permissions.BasePermission):

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        return request.user.groups.filter(name="Seller").exists()