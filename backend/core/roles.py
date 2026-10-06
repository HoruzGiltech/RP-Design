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
