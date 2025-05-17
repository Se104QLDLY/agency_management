from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from rest_framework_simplejwt.tokens import RefreshToken

def send_verification_email(user, request):
    refresh = RefreshToken.for_user(user)
    token = str(refresh.access_token)

    domain = request.get_host()
    url = reverse('verify-email')
    full_url = f"http://{domain}{url}?token={token}"

    subject = "Xác minh tài khoản đại lý của bạn"
    message = f"Chào {user.first_name},\n\nHãy xác minh tài khoản bằng liên kết sau:\n{full_url}\n\nCảm ơn bạn!"

    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])