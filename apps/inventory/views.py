from rest_framework import viewsets, filters
from .models import Unit, Item, Receipt, ReceiptDetail, Issue, IssueDetail
from .serializers import (
    UnitSerializer, ItemSerializer,
    ReceiptSerializer, ReceiptDetailSerializer,
    IssueSerializer, IssueDetailSerializer
)
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAuthenticated
from .permissions import IsAdminOrDistributor

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
    permission_classes = [IsAuthenticated, IsAdminOrDistributor]

class ReceiptDetailViewSet(viewsets.ModelViewSet):
    queryset = ReceiptDetail.objects.all()
    serializer_class = ReceiptDetailSerializer
    permission_classes = [IsAuthenticated, IsAdminOrDistributor]

class IssueViewSet(viewsets.ModelViewSet):
    queryset = Issue.objects.all()
    serializer_class = IssueSerializer
    permission_classes = [IsAuthenticated, IsAdminOrDistributor]

class IssueDetailViewSet(viewsets.ModelViewSet):
    queryset = IssueDetail.objects.all()
    serializer_class = IssueDetailSerializer
    permission_classes = [IsAuthenticated, IsAdminOrDistributor]
