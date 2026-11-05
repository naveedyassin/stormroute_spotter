from django.urls import path
from .views import CreateTripView

urlpatterns = [
    path("trips/", CreateTripView.as_view(), name="create-trip"),
]
