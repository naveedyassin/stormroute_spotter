from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse


def health_check(request):
    return JsonResponse({
        "application": "StormRoute API",
        "status": "running",
        "version": "1.0.0"
    })


urlpatterns = [
    path("", health_check, name="health-check"),
    path("admin/", admin.site.urls),
    path("api/", include("routing.urls")),
]