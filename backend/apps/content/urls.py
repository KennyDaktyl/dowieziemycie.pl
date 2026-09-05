from django.urls import path

from .views import (
    BlogPostDetailView,
    BlogPostListView,
    ContactInfoView,
    ContentPageDetailView,
    EventOfferDetailView,
    EventOfferListView,
    FixedRouteDetailView,
    FixedRouteListView,
    HomeContentView,
    LocalRouteDetailView,
    LocalRouteListView,
    TourDetailView,
    TourListView,
)

urlpatterns = [
    path("home-content/", HomeContentView.as_view(), name="home-content"),
    path("contact-info/", ContactInfoView.as_view(), name="contact-info"),
    path("tours/", TourListView.as_view(), name="tour-list"),
    path("tours/<slug:slug>/", TourDetailView.as_view(), name="tour-detail"),
    path("routes/", LocalRouteListView.as_view(), name="route-list"),
    path("routes/<slug:slug>/", LocalRouteDetailView.as_view(), name="route-detail"),
    path("fixed-routes/", FixedRouteListView.as_view(), name="fixed-route-list"),
    path("fixed-routes/<slug:slug>/", FixedRouteDetailView.as_view(), name="fixed-route-detail"),
    path("blog/", BlogPostListView.as_view(), name="blog-list"),
    path("blog/<slug:slug>/", BlogPostDetailView.as_view(), name="blog-detail"),
    path("content-pages/<slug:slug>/", ContentPageDetailView.as_view(), name="content-page-detail"),
    path("events/", EventOfferListView.as_view(), name="event-offer-list"),
    path("events/<slug:slug>/", EventOfferDetailView.as_view(), name="event-offer-detail"),
]
