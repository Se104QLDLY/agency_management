from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

schema_view = get_schema_view(
    openapi.Info(
        title="Agency Management API",
        default_version='v1',
        description="Tài liệu API cho phần mềm quản lý đại lý",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/accounts/', include('apps.accounts.urls')),
    path('api/agencies/', include('apps.agencies.urls')),
    path('api/inventory/', include('apps.inventory.urls')),
    path('api/finance/', include('apps.finance.urls')),
    path('api/regulations/', include('apps.regulations.urls')),
    path('api/dashboard/', include('apps.dashboard.urls')),

    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path('api/schema/', schema_view.without_ui(cache_timeout=0), name='openapi-schema'),
    path('api/docs/', schema_view.with_ui('swagger', cache_timeout=0), name='swagger-ui'),
    path('api/redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='redoc'),
]
