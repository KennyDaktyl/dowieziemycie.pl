from rest_framework.test import APIClient, APITestCase


class SiteScopingTests(APITestCase):
    """The two brands share one backend — a request is scoped to a site by
    the X-Site header (SiteMiddleware), defaulting to dowieziemycie when the
    header is missing so the not-yet-updated frontend keeps working."""

    def setUp(self):
        self.client = APIClient()

    def test_home_content_defaults_to_dowieziemycie_without_header(self):
        res = self.client.get("/api/home-content/")
        self.assertEqual(res.status_code, 200)
        self.assertIn("Bezpieczny", res.data["headline_pl"])

    def test_home_content_switches_with_x_site_header(self):
        res = self.client.get("/api/home-content/", HTTP_X_SITE="transfer247")
        self.assertEqual(res.status_code, 200)
        self.assertIn("Balice", res.data["headline_pl"])

    def test_home_content_unknown_site_header_falls_back_to_default(self):
        res = self.client.get("/api/home-content/", HTTP_X_SITE="not-a-real-site")
        self.assertEqual(res.status_code, 200)
        self.assertIn("Bezpieczny", res.data["headline_pl"])

    def test_fixed_routes_only_visible_for_transfer247(self):
        res_default = self.client.get("/api/fixed-routes/")
        self.assertEqual(res_default.status_code, 200)
        self.assertEqual(len(res_default.data), 0)

        res_transfer247 = self.client.get("/api/fixed-routes/", HTTP_X_SITE="transfer247")
        self.assertEqual(res_transfer247.status_code, 200)
        self.assertEqual(len(res_transfer247.data), 4)

    def test_tours_are_scoped_per_site(self):
        res_default = self.client.get("/api/tours/")
        default_slugs = {t["slug"] for t in res_default.data}
        self.assertNotIn("auschwitz-birkenau-transfer247", default_slugs)

        res_transfer247 = self.client.get("/api/tours/", HTTP_X_SITE="transfer247")
        transfer_slugs = {t["slug"] for t in res_transfer247.data}
        self.assertIn("auschwitz-birkenau-transfer247", transfer_slugs)
        self.assertIn("wieliczka-transfer247", transfer_slugs)

    def test_blog_posts_are_scoped_per_site(self):
        res_default = self.client.get("/api/blog/")
        self.assertEqual(len(res_default.data), 0)

        res_transfer247 = self.client.get("/api/blog/", HTTP_X_SITE="transfer247")
        self.assertEqual(len(res_transfer247.data), 4)
