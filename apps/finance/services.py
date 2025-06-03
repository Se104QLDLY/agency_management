import io
import pandas as pd
from django.http import HttpResponse
from .models import Payment
from apps.agencies.models import Agency
from reportlab.pdfgen import canvas
from django.utils.timezone import now

def generate_payment_excel(start_date, end_date):
    payments = Payment.objects.filter(payment_date__range=[start_date, end_date])
    data = [{
        'Ngày thu': p.payment_date,
        'Đại lý': p.agency.name,
        'Người thu': p.user.username if p.user else '',
        'Số tiền': float(p.amount_collected),
    } for p in payments]

    df = pd.DataFrame(data)
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='BaoCao', index=False)
    buffer.seek(0)
    return buffer

def generate_debt_report_pdf():
    agencies = Agency.objects.all()
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer)
    p.setFont("Helvetica-Bold", 14)
    p.drawString(100, 800, "BÁO CÁO CÔNG NỢ ĐẠI LÝ")
    p.setFont("Helvetica", 10)

    y = 770
    for a in agencies:
        p.drawString(80, y, f"{a.name} - Nợ: {a.debt} VNĐ")
        y -= 20
        if y < 50:
            p.showPage()
            y = 800

    p.showPage()
    p.save()
    buffer.seek(0)
    return buffer
