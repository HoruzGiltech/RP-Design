"""
Clases base que reutilizan las demás apps.

Todas son abstractas: no crean tablas propias, solo aportan campos
y comportamiento a los modelos que heredan de ellas.
"""
from django.db import models


class TimeStampedModel(models.Model):
    """Guarda cuándo se creó y cuándo se modificó el registro."""

    created_at = models.DateTimeField("creado", auto_now_add=True)
    updated_at = models.DateTimeField("actualizado", auto_now=True)

    class Meta:
        abstract = True


class OrderedModel(models.Model):
    """Permite ordenar los registros a mano (arrastrando en el panel)."""

    order = models.PositiveIntegerField("orden", default=0, db_index=True)

    class Meta:
        abstract = True
        ordering = ["order"]


class VisibleModel(models.Model):
    """Interruptor para ocultar algo del sitio sin tener que borrarlo."""

    is_visible = models.BooleanField("mostrar en el sitio", default=True)

    class Meta:
        abstract = True


class SingletonModel(models.Model):
    """
    Modelo con un único registro (por ejemplo, la Portada).

    Siempre usa pk=1: así es imposible crear un segundo registro,
    porque guardar "otro" solo sobrescribe el que ya existe.
    """

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # No se borra: el sitio necesita que el registro exista siempre.
        # Se devuelve lo mismo que Django cuando no borra nada.
        return 0, {}

    @classmethod
    def load(cls):
        """Devuelve el registro único y lo crea si todavía no existe."""
        instance, _created = cls.objects.get_or_create(pk=1)
        return instance
