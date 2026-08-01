import io
import tempfile

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from PIL import Image
from rest_framework.test import APIClient, APITestCase

from apps.fleet.models import Vehicle

from .models import FixedRoute, FixedRoutePhoto, FixedRouteVehiclePrice


def _make_test_image_upload(name="photo.png", size=(800, 600), color=(200, 50, 50)) -> SimpleUploadedFile:
    buffer = io.BytesIO()
    Image.new("RGB", size, color).save(buffer, format="PNG")
    return SimpleUploadedFile(name, buffer.getvalue(), content_type="image/png")


class VehiclePricingTests(APITestCase):
    """Price is per real vehicle from the fleet — however many vehicles a
    route/tour has been priced for, not a hardcoded pair of fields. See
    migration 0019 for why this replaced price_from/price_large_vehicle."""

    def setUp(self):
        self.client = APIClient()
        self.route = FixedRoute.objects.create(
            site="transfer247", slug="test-route", name_pl="Test", name_en="Test",
        )

    def test_route_with_no_prices_reports_none(self):
        res = self.client.get("/api/fixed-routes/test-route/", HTTP_X_SITE="transfer247")
        self.assertEqual(res.status_code, 200)
        self.assertIsNone(res.data["price_from"])
        self.assertEqual(res.data["vehicle_prices"], [])

    def test_adding_a_third_vehicle_just_adds_a_third_price_row(self):
        """The whole point: this isn't capped at two."""
        names = ["Toyota Auris Hybrid", "Ford Tourneo Custom", "Mercedes Vito"]
        for i, name in enumerate(names):
            vehicle = Vehicle.objects.create(name=name, plate=f"TEST{i}")
            FixedRouteVehiclePrice.objects.create(route=self.route, vehicle=vehicle, price=100 + i * 50)

        res = self.client.get("/api/fixed-routes/test-route/", HTTP_X_SITE="transfer247")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.data["vehicle_prices"]), 3)
        self.assertEqual({vp["vehicle_name"] for vp in res.data["vehicle_prices"]}, set(names))
        self.assertEqual(float(res.data["price_from"]), 100.0)


@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class ImageProcessingTests(TestCase):
    """Every upload goes through the same WebP + thumbnail pipeline — see
    common/imaging.py. No model should be able to opt out. Uses an isolated
    MEDIA_ROOT so test uploads don't land in the real media/ directory."""

    def test_gallery_photo_is_converted_to_webp_with_a_thumbnail(self):
        route = FixedRoute.objects.create(
            site="transfer247", slug="img-route", name_pl="Test", name_en="Test",
        )
        photo = FixedRoutePhoto.objects.create(route=route, image=_make_test_image_upload())

        self.assertTrue(photo.image.name.endswith(".webp"))
        self.assertTrue(photo.thumbnail.name.endswith(".webp"))

        thumb = Image.open(photo.thumbnail)
        self.assertLessEqual(thumb.width, 480)
        self.assertLessEqual(thumb.height, 480)


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
        self.assertIn("lotniska", res.data["headline_pl"])

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
