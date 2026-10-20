from xml.etree import ElementTree

from django.test import TestCase, override_settings

from core.tests.helpers import TempMediaMixin
from projects.tests.test_models import create_project

NAMESPACE = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}


@override_settings(FRONTEND_URL="https://rpdesignve.com/")
class SitemapTests(TempMediaMixin, TestCase):
    def get_locs(self):
        response = self.client.get("/sitemap.xml")
        self.assertEqual(response.status_code, 200)
        root = ElementTree.fromstring(response.content)  # falla si el XML es inválido
        return response, [loc.text for loc in root.findall("s:url/s:loc", NAMESPACE)]

    def test_returns_xml_with_fixed_pages(self):
        response, locs = self.get_locs()
        self.assertIn("application/xml", response["Content-Type"])
        for path in ["/", "/proyectos", "/terminos", "/privacidad"]:
            self.assertIn(f"https://rpdesignve.com{path}", locs)

    def test_published_project_is_listed_with_lastmod(self):
        create_project(title="Cocina Carlos", is_published=True)
        response, locs = self.get_locs()
        self.assertIn("https://rpdesignve.com/proyectos/cocina-carlos", locs)
        self.assertIn(b"<lastmod>", response.content)

    def test_draft_project_is_not_listed(self):
        create_project(title="Borrador secreto", is_published=False)
        _, locs = self.get_locs()
        self.assertFalse([loc for loc in locs if "borrador" in loc])

    def test_urls_have_no_double_slash(self):
        _, locs = self.get_locs()
        for loc in locs:
            self.assertNotIn("//", loc.replace("https://", ""))

    def test_post_is_not_allowed(self):
        self.assertEqual(self.client.post("/sitemap.xml").status_code, 405)


class NoIndexTests(TestCase):
    def test_api_is_noindex(self):
        response = self.client.get("/api/projects/")
        self.assertEqual(response["X-Robots-Tag"], "noindex")

    def test_sitemap_is_not_noindex(self):
        response = self.client.get("/sitemap.xml")
        self.assertNotIn("X-Robots-Tag", response)
