from django.db import connection, models
from django.test import TestCase

from core.models import SingletonModel


class SampleSingleton(SingletonModel):
    """Modelo solo para estos tests: SingletonModel es abstracto y no tiene tabla."""

    title = models.CharField(max_length=50, default="")

    class Meta:
        app_label = "core"


class SingletonModelTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # El modelo de prueba no tiene migración, así que su tabla se crea aquí.
        # Al terminar los tests, Django deshace la transacción y la tabla desaparece.
        with connection.schema_editor() as editor:
            editor.create_model(SampleSingleton)

    def test_save_always_uses_pk_1(self):
        instance = SampleSingleton(title="uno")
        instance.save()

        self.assertEqual(instance.pk, 1)

    def test_saving_a_second_instance_overwrites_the_first(self):
        SampleSingleton(title="uno").save()
        SampleSingleton(title="dos").save()

        self.assertEqual(SampleSingleton.objects.count(), 1)
        self.assertEqual(SampleSingleton.objects.get().title, "dos")

    def test_delete_does_not_remove_the_record(self):
        instance = SampleSingleton.load()

        instance.delete()

        self.assertEqual(SampleSingleton.objects.count(), 1)

    def test_load_creates_the_record_when_missing(self):
        self.assertEqual(SampleSingleton.objects.count(), 0)

        instance = SampleSingleton.load()

        self.assertEqual(instance.pk, 1)
        self.assertEqual(SampleSingleton.objects.count(), 1)

    def test_load_returns_the_existing_record(self):
        SampleSingleton(title="guardado").save()

        self.assertEqual(SampleSingleton.load().title, "guardado")
