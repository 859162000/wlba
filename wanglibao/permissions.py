from rest_framework.permissions import BasePermission


class AllowAnyPostOnlyAdminList(BasePermission):
    def has_permission(self, request, view):
        if request.method == 'GET':
            if request.user.is_superuser:
                return True
        elif request.method == 'POST':
            return True

        return False