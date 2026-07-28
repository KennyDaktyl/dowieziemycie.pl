from django.urls import path

from .views import (
    ContentPageDetailView,
    HomeContentView,
    LocalRouteDetailView,
    LocalRouteListView,
    TourDetailView,
    TourListView,
)

urlpatterns = [
    path("home-content/", HomeContentView.as_view(), name="home-content"),
    path("tours/", TourListView.as_view(), name="tour-list"),
    path("tours/<slug:slug>/", TourDetailView.as_view(), name="tour-detail"),
    path("routes/", LocalRouteListView.as_view(), name="route-list"),
    path("routes/<slug:slug>/", LocalRouteDetailView.as_view(), name="route-detail"),
    path("content-pages/<slug:slug>/", ContentPageDetailView.as_view(), name="content-page-detail"),
]
