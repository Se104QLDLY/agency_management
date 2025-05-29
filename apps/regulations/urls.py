from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RegulationViewSet

router = DefaultRouter()
router.register(r'regulations', RegulationViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
