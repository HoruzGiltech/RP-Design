"""Piezas que comparten los formularios del panel."""
import json

from django.db import models

from core.validators import get_upload_rules


class FileCheckMixin:
    """
    Hace que el navegador revise cada archivo en el momento de elegirlo
    (specs-007, RF-56).

    Sin esto, si una sola foto pasa del tamaño máximo, el formulario vuelve
    con el error y se pierden TODAS las fotos elegidas: el servidor no puede
    volver a rellenar un campo de archivo.

    A cada campo de archivo le agrega el atributo data-upload-rules con sus
    formatos y tamaños permitidos. El script core/admin-file-check.js lo lee.
    Sirve para clases del panel (ModelAdmin) y para sus tablas internas (inlines).
    """

    class Media:
        js = ("core/admin-file-check.js",)

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        form_field = super().formfield_for_dbfield(db_field, request, **kwargs)
        # form_field es None cuando el campo no se muestra en el formulario
        if form_field is None or not isinstance(db_field, models.FileField):
            return form_field

        rules = self._get_rules(db_field)
        if rules:
            form_field.widget.attrs["data-upload-rules"] = json.dumps(rules)
        return form_field

    def _get_rules(self, db_field):
        """Junta las reglas de los validadores del campo: {"jpg": 5, "mp4": 50, ...}"""
        rules = {}
        for validator in db_field.validators:
            rules.update(get_upload_rules(validator))
        return rules
