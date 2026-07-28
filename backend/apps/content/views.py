from rest_framework import generics
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import ContentPage, HomeContent, LocalRoute, Tour
from .serializers import (
    ContentPageSerializer,
    HomeContentSerializer,
    LocalRouteSerializer,
    TourSerializer,
)


class HomeContentView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        content, _ = HomeContent.objects.get_or_create(pk=1)
        return Response(HomeContentSerializer(content).data)


class TourListView(generics.ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = TourSerializer
    queryset = Tour.objects.filter(is_published=True)


class TourDetailView(generics.RetrieveAPIView):
    permission_classes = [AllowAny]
    serializer_class = TourSerializer
    queryset = Tour.objects.filter(is_published=True)
    lookup_field = "slug"


class LocalRouteListView(generics.ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = LocalRouteSerializer
    queryset = LocalRoute.objects.filter(is_published=True)


class LocalRouteDetailView(generics.RetrieveAPIView):
    permission_classes = [AllowAny]
    serializer_class = LocalRouteSerializer
    queryset = LocalRoute.objects.filter(is_published=True)
    lookup_field = "slug"


class ContentPageDetailView(generics.RetrieveAPIView):
    permission_classes = [AllowAny]
    serializer_class = ContentPageSerializer
    queryset = ContentPage.objects.filter(is_published=True)
    lookup_field = "slug"
