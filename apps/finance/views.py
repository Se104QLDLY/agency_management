from rest_framework import viewsets, filters
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.http import FileResponse, HttpResponseBadRequest
from django.utils.dateparse import parse_date

from .models import Payment
from .serializers import PaymentSerializer
from .permissions import IsDistributorOrAdmin
from .services import generate_payment_excel, generate_debt_report_pdf


class PaymentViewSet(viewsets.ModelViewSet):
    """
    API CRUD phiếu thu tiền
    """
    queryset = Payment.objects.select_related('agency', 'user').all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated, IsDistributorOrAdmin]

    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['agency', 'payment_date']
    search_fields = ['agency__name', 'user__username']


class PaymentExcelReportView(APIView):
    """
    Xuất báo cáo phiếu thu ra Excel (.xlsx)
    Yêu cầu query params: start_date, end_date (YYYY-MM-DD)
    """
    permission_classes = [IsAuthenticated, IsDistributorOrAdmin]

    def get(self, request):
        start = request.GET.get('start_date')
        end = request.GET.get('end_date')
        if not start or not end:
            return HttpResponseBadRequest("Cần truyền start_date và end_date (ví dụ: ?start_date=2024-01-01&end_date=2024-12-31)")

        excel_file = generate_payment_excel(parse_date(start), parse_date(end))
        return FileResponse(excel_file, as_attachment=True, filename="bao_cao_thu_tien.xlsx")


class DebtPDFReportView(APIView):
    """
    Xuất báo cáo công nợ (tổng nợ các đại lý) dạng PDF
    """
    permission_classes = [IsAuthenticated, IsDistributorOrAdmin]

    def get(self, request):
        pdf = generate_debt_report_pdf()
        return FileResponse(pdf, as_attachment=True, filename="bao_cao_cong_no.pdf")
