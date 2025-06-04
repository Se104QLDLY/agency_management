from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AgencyViewSet, AgencyTypeViewSet, DistrictViewSet

router = DefaultRouter()
router.register(r'agencies', AgencyViewSet)
router.register(r'agency-types', AgencyTypeViewSet)
router.register(r'districts', DistrictViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
