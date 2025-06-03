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

    subject = "Xác minh tài khoản"
    message = f"Xin chào {user.username},\n\nVui lòng xác minh tài khoản tại:\n{full_url}"

    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])
