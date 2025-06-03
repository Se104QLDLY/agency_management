from rest_framework import viewsets, filters
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.http import FileResponse, HttpResponseBadRequest
from django.utils.dateparse import parse_date

from .models import Payment
from .serializers import PaymentSerializer
from .permissions import IsAdminOrDistributor, IsAgencySelfOnly
from .services import generate_payment_excel, generate_debt_report_pdf


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.select_related('agency', 'user').all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]

    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['agency', 'payment_date']
    search_fields = ['agency__name', 'user__username']

    def get_queryset(self):
        user = self.request.user
        if user.role == 'A3':
            return self.queryset.filter(agency__in=user.agency_set.all())
        return self.queryset

    def get_permissions(self):
        if self.action in ['create', 'update', 'destroy']:
            return [IsAuthenticated(), IsAdminOrDistributor()]
        return [IsAuthenticated()]


class PaymentExcelReportView(APIView):
    permission_classes = [IsAuthenticated, IsAdminOrDistributor]

    def get(self, request):
        start = request.GET.get('start_date')
        end = request.GET.get('end_date')
        if not start or not end:
            return HttpResponseBadRequest("Cần truyền start_date và end_date")
        excel_file = generate_payment_excel(parse_date(start), parse_date(end))
        return FileResponse(excel_file, as_attachment=True, filename="bao_cao_thu_tien.xlsx")


class DebtPDFReportView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        buffer = generate_debt_report_pdf()
        return FileResponse(buffer, as_attachment=True, filename="bao_cao_cong_no.pdf")
