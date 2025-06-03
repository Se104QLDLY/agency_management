from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Unit, Item, Receipt, ReceiptDetail, Issue, IssueDetail
from .serializers import *
from .permissions import *

class UnitViewSet(viewsets.ModelViewSet):
    queryset = Unit.objects.all()
    serializer_class = UnitSerializer
    permission_classes = [IsAuthenticated, CanViewInventory]

class ItemViewSet(viewsets.ModelViewSet):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    permission_classes = [IsAuthenticated, CanViewInventory]

class ReceiptViewSet(viewsets.ModelViewSet):
    queryset = Receipt.objects.all()
    serializer_class = ReceiptSerializer
    permission_classes = [IsAuthenticated, CanManageReceipt]

class ReceiptDetailViewSet(viewsets.ModelViewSet):
    queryset = ReceiptDetail.objects.all()
    serializer_class = ReceiptDetailSerializer
    permission_classes = [IsAuthenticated, CanManageReceipt]

class IssueViewSet(viewsets.ModelViewSet):
    queryset = Issue.objects.all()
    serializer_class = IssueSerializer
    permission_classes = [IsAuthenticated, CanManageIssue]

class IssueDetailViewSet(viewsets.ModelViewSet):
    queryset = IssueDetail.objects.all()
    serializer_class = IssueDetailSerializer
    permission_classes = [IsAuthenticated, CanManageIssue]
