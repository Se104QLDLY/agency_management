from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Regulation
from .serializers import RegulationSerializer
from .permissions import IsAdmin

class RegulationViewSet(viewsets.ModelViewSet):
    queryset = Regulation.objects.all()
    serializer_class = RegulationSerializer
    permission_classes = [IsAuthenticated, IsAdmin]

    def perform_create(self, serializer):
        serializer.save(updated_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)
