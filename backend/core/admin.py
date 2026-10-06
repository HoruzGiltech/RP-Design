from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

User = get_user_model()

# Campos que solo puede tocar el superusuario (el desarrollador)
SUPERUSER_ONLY_FIELDS = ("is_superuser", "user_permissions")

admin.site.unregister(User)


@admin.register(User)
class PanelUserAdmin(UserAdmin):
    """
    Gestión de usuarios del panel.

    El rol Admin puede crear usuarios y asignarles un grupo, pero no puede
    convertirse en superusuario ni dar permisos sueltos: sin este control,
    cualquiera que pueda editar usuarios podría darse acceso total.
    """

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super().get_readonly_fields(request, obj)
        if request.user.is_superuser:
            return readonly_fields
        return (*readonly_fields, *SUPERUSER_ONLY_FIELDS)

    def has_change_permission(self, request, obj=None):
        if self._is_superuser_protected(request, obj):
            return False
        return super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        if self._is_superuser_protected(request, obj):
            return False
        return super().has_delete_permission(request, obj)

    def _is_superuser_protected(self, request, obj):
        """La cuenta del desarrollador solo la modifica otro superusuario."""
        return obj is not None and obj.is_superuser and not request.user.is_superuser
