from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import BlogPost, ContentPage, FixedRoute, HomeContent, LocalRoute, Tour
from .serializers import (
    BlogPostSerializer,
    ContentPageSerializer,
    FixedRouteSerializer,
    HomeContentSerializer,
    LocalRouteSerializer,
    TourSerializer,
)


class HomeContentView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        content = get_object_or_404(HomeContent, site=request.site_code)
        return Response(HomeContentSerializer(content).data)


class TourListView(generics.ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = TourSerializer

    def get_queryset(self):
        return Tour.objects.filter(is_published=True, site=self.request.site_code)


class TourDetailView(generics.RetrieveAPIView):
    permission_classes = [AllowAny]
    serializer_class = TourSerializer
    lookup_field = "slug"

    def get_queryset(self):
        return Tour.objects.filter(is_published=True, site=self.request.site_code)


class LocalRouteListView(generics.ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = LocalRouteSerializer
    queryset = LocalRoute.objects.filter(is_published=True)


class LocalRouteDetailView(generics.RetrieveAPIView):
    permission_classes = [AllowAny]
    serializer_class = LocalRouteSerializer
    queryset = LocalRoute.objects.filter(is_published=True)
    lookup_field = "slug"


class FixedRouteListView(generics.ListAPIView):
    """GET /api/fixed-routes/ — transfer247's point-to-point routes, site-filtered."""

    permission_classes = [AllowAny]
    serializer_class = FixedRouteSerializer

    def get_queryset(self):
        return FixedRoute.objects.filter(is_published=True, site=self.request.site_code)


class FixedRouteDetailView(generics.RetrieveAPIView):
    permission_classes = [AllowAny]
    serializer_class = FixedRouteSerializer
    lookup_field = "slug"

    def get_queryset(self):
        return FixedRoute.objects.filter(is_published=True, site=self.request.site_code)


class BlogPostListView(generics.ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = BlogPostSerializer

    def get_queryset(self):
        return BlogPost.objects.filter(is_published=True, site=self.request.site_code)


class BlogPostDetailView(generics.RetrieveAPIView):
    permission_classes = [AllowAny]
    serializer_class = BlogPostSerializer
    lookup_field = "slug"

    def get_queryset(self):
        return BlogPost.objects.filter(is_published=True, site=self.request.site_code)


class ContentPageDetailView(generics.RetrieveAPIView):
    permission_classes = [AllowAny]
    serializer_class = ContentPageSerializer
    lookup_field = "slug"

    def get_queryset(self):
        return ContentPage.objects.filter(is_published=True, site=self.request.site_code)
