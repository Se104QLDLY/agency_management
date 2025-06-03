from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Regulation
from .serializers import RegulationSerializer
from .permissions import IsAdminOnly

class RegulationViewSet(viewsets.ModelViewSet):
    queryset = Regulation.objects.all()
    serializer_class = RegulationSerializer
    permission_classes = [IsAuthenticated, IsAdminOnly]
