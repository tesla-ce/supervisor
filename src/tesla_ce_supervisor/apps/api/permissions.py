#  Copyright (c) 2020 Xavier Baró
#
#      This program is free software: you can redistribute it and/or modify
#      it under the terms of the GNU Affero General Public License as
#      published by the Free Software Foundation, either version 3 of the
#      License, or (at your option) any later version.
#
#      This program is distributed in the hope that it will be useful,
#      but WITHOUT ANY WARRANTY; without even the implied warranty of
#      MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#      GNU Affero General Public License for more details.
#
#      You should have received a copy of the GNU Affero General Public License
#      along with this program.  If not, see <https://www.gnu.org/licenses/>.
""" TeSLA Supervisor API permissions module """
from rest_framework import permissions


class IsAuthenticated(permissions.BasePermission):
    """
        Base Permission
    """
    def has_permission(self, request, view):
        return True


class AdminPermission(IsAuthenticated):
    """
        Admin permission
    """
    def has_permission(self, request, view):
        return request.user.is_staff


class AlwaysAllowPermission(IsAuthenticated):
    """
        Admin permission
    """
    def has_permission(self, request, view):
        return True


class ConfigPermission(IsAuthenticated):
    def has_permission(self, request, view):
        if view.action == 'list' or view.action == 'create':
            return True
        else:
            return request.user.is_staff
