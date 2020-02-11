from rest_framework import permissions
from rolepermissions.checkers import has_role

from myparking.roles import Agent, Driver


class IsAgent(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return has_role(request.user, Agent)

    def has_permission(self, request, view):
        return has_role(request.user, Agent)


class IsDriver(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return has_role(request.user, Driver)
    def has_permission(self, request, view):
        return has_role(request.user, Driver)


class IsAdminUser(permissions.BasePermission):

    def has_permission(self, request, view):
        return request.user and request.user.is_staff

    def has_object_permission(self, request, view, obj):
        return request.user and request.user.is_staff
