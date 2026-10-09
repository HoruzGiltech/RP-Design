from decimal import Decimal

from django.core.management import call_command
from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.test import TransactionTestCase

BEFORE = [("quotes", "0006_quote_items")]
AFTER = [("quotes", "0007_migrate_quote_items")]


def migrate_to(target):
    """Lleva la base de datos a una migración y devuelve los modelos tal como eran ahí."""
    executor = MigrationExecutor(connection)
    executor.migrate(target)
    return executor.loader.project_state(target).apps


class QuoteItemsMigrationTests(TransactionTestCase):
    """
    La migración 0007 convierte cada cotización antigua (una sola área, guardada
    en la propia cotización) en una cotización de un renglón.

    Es TransactionTestCase porque el test cambia las tablas: retrocede la base
    de datos a como estaba antes de specs-003 y la vuelve a avanzar.
    """

    def tearDown(self):
        # La base de datos queda al día para los tests que vengan después
        call_command("migrate", verbosity=0)

    def create_old_quote(self, old_apps, **fields):
        Quote = old_apps.get_model("quotes", "Quote")
        RemodelArea = old_apps.get_model("quotes", "RemodelArea")
        area, _ = RemodelArea.objects.get_or_create(slug="cocina", defaults={"name": "Cocina"})
        values = {
            "name": "Ana Pérez",
            "email": "ana@mail.com",
            "phone": "+584121234567",
            "area": area,
            "square_meters": Decimal("12.5"),
            "price_per_m2_snapshot": Decimal("100"),
            "estimated_price": Decimal("1250"),
            "whatsapp_message": "Hola RP Design, quiero una cotización",
        }
        values.update(fields)
        return Quote.objects.create(**values)

    def test_old_quote_becomes_a_quote_with_one_item(self):
        old_apps = migrate_to(BEFORE)
        old_quote = self.create_old_quote(old_apps, area_other="Terraza")

        new_apps = migrate_to(AFTER)

        item = new_apps.get_model("quotes", "QuoteItem").objects.get()
        self.assertEqual(item.quote_id, old_quote.pk)
        self.assertEqual(item.area.slug, "cocina")
        self.assertEqual(item.area_other, "Terraza")
        self.assertEqual(item.square_meters, Decimal("12.5"))
        self.assertEqual(item.price_per_m2_snapshot, Decimal("100"))
        self.assertEqual(item.subtotal, Decimal("1250"))

    def test_quote_to_be_quoted_keeps_its_item_without_price(self):
        old_apps = migrate_to(BEFORE)
        self.create_old_quote(old_apps, price_per_m2_snapshot=None, estimated_price=None)

        new_apps = migrate_to(AFTER)

        item = new_apps.get_model("quotes", "QuoteItem").objects.get()
        self.assertIsNone(item.price_per_m2_snapshot)
        self.assertIsNone(item.subtotal)

    def test_every_old_quote_gets_exactly_one_item(self):
        old_apps = migrate_to(BEFORE)
        self.create_old_quote(old_apps, name="Primera")
        self.create_old_quote(old_apps, name="Segunda")

        new_apps = migrate_to(AFTER)

        Quote = new_apps.get_model("quotes", "Quote")
        QuoteItem = new_apps.get_model("quotes", "QuoteItem")
        self.assertEqual(QuoteItem.objects.count(), 2)
        for quote in Quote.objects.all():
            self.assertEqual(QuoteItem.objects.filter(quote=quote).count(), 1)
