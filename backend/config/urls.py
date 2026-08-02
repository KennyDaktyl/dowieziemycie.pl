from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/", include("apps.accounts.urls")),
    path("api/fleet/", include("apps.fleet.urls")),
    path("api/", include("apps.bookings.urls")),
    path("api/", include("apps.content.urls")),
    path("api/tracking/", include("apps.tracking.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
