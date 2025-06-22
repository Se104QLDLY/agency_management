from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RegulationViewSet

# Create router for ViewSets
router = DefaultRouter()
router.register(r"regulation", RegulationViewSet, basename="regulation")

urlpatterns = [
    # Regulation API endpoints
    # Following docs/api.md structure:
    # GET          /api/v1/regulation/
    # GET/PUT      /api/v1/regulation/{key}/
    # GET          /api/v1/regulation/history/
    path("", include(router.urls)),
]
