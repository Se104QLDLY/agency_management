from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .models import Account, UserProfile, LoginHistory
from .serializers import (
    AccountSerializer, UserProfileSerializer,
    RegisterSerializer, LoginHistorySerializer
)
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .utils import send_verification_email
from rest_framework_simplejwt.tokens import AccessToken

class AccountViewSet(viewsets.ModelViewSet):
    queryset = Account.objects.all()
    serializer_class = AccountSerializer
    permission_classes = [IsAuthenticated]

class UserProfileViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

class LoginHistoryViewSet(viewsets.ModelViewSet):
    queryset = LoginHistory.objects.all()
    serializer_class = LoginHistorySerializer
    permission_classes = [IsAdminUser]

class RegisterAPIView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        send_verification_email(user, request)
        return Response({"detail": "Tạo tài khoản thành công. Kiểm tra email để xác minh."}, status=status.HTTP_201_CREATED)

class VerifyEmailAPIView(APIView):
    def get(self, request):
        token = request.GET.get('token')
        try:
            access_token = AccessToken(token)
            user_id = access_token['user_id']
            user = Account.objects.get(id=user_id)
            user.is_active = True
            user.save()
            return Response({'detail': 'Email xác minh thành công.'})
        except Exception:
            return Response({'detail': 'Token không hợp lệ hoặc đã hết hạn.'}, status=400)
