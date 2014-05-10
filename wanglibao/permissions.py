from rest_framework.permissions import BasePermission, SAFE_METHODS


class AllowAnyPostOnlyAdminList(BasePermission):
    def has_permission(self, request, view):
        if request.method == 'GET':
            if request.user.is_superuser:
                return True
        elif request.method == 'POST':
            return True

        return False


class IsAdminUserOrReadOnly(BasePermission):
    """
    Allows access only to admin users.
    """

    def has_permission(self, request, view):
        if request.user and request.user.is_staff or request.method in SAFE_METHODS:
            return True
        return False