from rest_framework import viewsets, filters
from .models import Unit, Item, Receipt, ReceiptDetail, Issue, IssueDetail
from .serializers import *
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAuthenticated
from .permissions import IsAdminOrDistributor, IsAgencyItselfOrReadOnly

class UnitViewSet(viewsets.ModelViewSet):
    queryset = Unit.objects.all()
    serializer_class = UnitSerializer
    permission_classes = [IsAuthenticated]

class ItemViewSet(viewsets.ModelViewSet):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'description']

class ReceiptViewSet(viewsets.ModelViewSet):
    queryset = Receipt.objects.all()
    serializer_class = ReceiptSerializer

    def get_permissions(self):
        if self.request.user.role in ['A1', 'A2']:
            return [IsAuthenticated(), IsAdminOrDistributor()]
        return [IsAuthenticated()]

class ReceiptDetailViewSet(viewsets.ModelViewSet):
    queryset = ReceiptDetail.objects.all()
    serializer_class = ReceiptDetailSerializer
    permission_classes = [IsAuthenticated, IsAdminOrDistributor]

class IssueViewSet(viewsets.ModelViewSet):
    queryset = Issue.objects.all()
    serializer_class = IssueSerializer

    def get_permissions(self):
        if self.request.user.role in ['A1', 'A2']:
            return [IsAuthenticated(), IsAdminOrDistributor()]
        elif self.request.user.role == 'A3':
            return [IsAuthenticated(), IsAgencyItselfOrReadOnly()]
        return [IsAuthenticated()]

class IssueDetailViewSet(viewsets.ModelViewSet):
    queryset = IssueDetail.objects.all()
    serializer_class = IssueDetailSerializer
    permission_classes = [IsAuthenticated]
