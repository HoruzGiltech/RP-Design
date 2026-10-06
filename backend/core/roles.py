"""
Roles del panel.

Cada rol es un grupo de Django con sus permisos. A los usuarios se les
asigna un grupo; no se dan permisos sueltos usuario por usuario.
"""

ADMIN_GROUP = "Admin"
VIEWER_GROUP = "Viewer"

# Apps cuyo contenido gestiona el cliente desde el panel
CONTENT_APPS = ["projects", "quotes", "site_content"]

# Además del contenido, el rol Admin gestiona usuarios y grupos
USER_MODELS = ["user", "group"]


def ensure_permissions_exist(apps):
    """
    Django crea los permisos al terminar TODAS las migraciones.
    Las migraciones de grupos los necesitan antes, así que se le pide crearlos ya.
    """
    # Se importa aquí y no arriba: al cargar este archivo Django aún puede no estar listo
    from django.contrib.auth.management import create_permissions

    for app_config in apps.get_app_configs():
        app_config.models_module = True
        create_permissions(app_config, apps=apps, verbosity=0)
        app_config.models_module = None


def assign_group_permissions(apps):
    """
    Crea los grupos Admin y Viewer (si no existen) y les da sus permisos.

    Se llama desde las migraciones de core. Si se agrega un modelo nuevo,
    basta una migración nueva que vuelva a llamar a esta función.
    """
    ensure_permissions_exist(apps)

    Group = apps.get_model("auth", "Group")
    Permission = apps.get_model("auth", "Permission")

    content_permissions = Permission.objects.filter(content_type__app_label__in=CONTENT_APPS)
    user_permissions = Permission.objects.filter(
        content_type__app_label="auth", content_type__model__in=USER_MODELS
    )

    admin_group, _created = Group.objects.get_or_create(name=ADMIN_GROUP)
    admin_group.permissions.set(list(content_permissions) + list(user_permissions))

    viewer_group, _created = Group.objects.get_or_create(name=VIEWER_GROUP)
    viewer_group.permissions.set(content_permissions.filter(codename__startswith="view_"))
