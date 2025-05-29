from rest_framework import viewsets
from .models import Regulation
from .serializers import RegulationSerializer
from .permissions import IsAdmin
from rest_framework.permissions import IsAuthenticated

class RegulationViewSet(viewsets.ModelViewSet):
    queryset = Regulation.objects.all()
    serializer_class = RegulationSerializer
    permission_classes = [IsAuthenticated, IsAdmin]
