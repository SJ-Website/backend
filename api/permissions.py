from rest_framework import permissions
from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsOwner(BasePermission):
    """
    Permission class for owners only.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'owner'


class IsCustomer(BasePermission):
    """
    Permission class for customers only.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'customer'
