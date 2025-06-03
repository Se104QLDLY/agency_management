from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAuthenticated

from .models import Agency, AgencyType, District
from .serializers import AgencySerializer, AgencyTypeSerializer, DistrictSerializer
from .permissions import IsAdmin, IsDistributor, IsAdminOrDistributor, IsAdminDistributorAgency

class AgencyViewSet(viewsets.ModelViewSet):
    queryset = Agency.objects.all()
    serializer_class = AgencySerializer
    permission_classes = [IsAuthenticated, IsAdminOrDistributor]  # A1 và A2 được quản lý đại lý
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['district', 'agency_type']
    search_fields = ['name', 'email', 'phone']

class AgencyTypeViewSet(viewsets.ModelViewSet):
    queryset = AgencyType.objects.all()
    serializer_class = AgencyTypeSerializer
    permission_classes = [IsAuthenticated, IsAdmin]  # chỉ Admin

class DistrictViewSet(viewsets.ModelViewSet):
    queryset = District.objects.all()
    serializer_class = DistrictSerializer
    permission_classes = [IsAuthenticated, IsAdmin]  # chỉ Admin
