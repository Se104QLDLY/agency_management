from rest_framework import viewsets, filters
from .models import Agency, AgencyType, District
from .serializers import AgencySerializer, AgencyTypeSerializer, DistrictSerializer
from .permissions import IsAdmin, IsDistributor, IsAdminOrDistributor
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

class AgencyViewSet(viewsets.ModelViewSet):
    queryset = Agency.objects.all()
    serializer_class = AgencySerializer
    permission_classes = [IsAuthenticated, IsAdminOrDistributor]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['district', 'agency_type']
    search_fields = ['name', 'email', 'phone']

class AgencyTypeViewSet(viewsets.ModelViewSet):
    queryset = AgencyType.objects.all()
    serializer_class = AgencyTypeSerializer
    permission_classes = [IsAuthenticated, IsAdminOrDistributor]

class DistrictViewSet(viewsets.ModelViewSet):
    queryset = District.objects.all()
    serializer_class = DistrictSerializer
    permission_classes = [IsAuthenticated, IsAdminOrDistributor]
