from django.urls import path

from .views import TrackByCodeView

urlpatterns = [
    path("track-by-code/", TrackByCodeView.as_view(), name="track-by-code"),
]
