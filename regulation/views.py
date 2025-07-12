from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import Regulation
from .serializers import (
    RegulationListSerializer, RegulationDetailSerializer, 
    RegulationUpdateSerializer, RegulationCreateSerializer, RegulationHistorySerializer
)
from authentication.permissions import CookieJWTAuthentication, ConfigPermission, ConfigReadPermission


class RegulationViewSet(viewsets.ViewSet):
    """
    ViewSet for managing system regulations
    GET /api/v1/regulation/ - List all regulations (staff can read)
    POST /api/v1/regulation/ - Create new regulation (admin only)
    GET /api/v1/regulation/{key}/ - Get regulation by key (staff can read)
    PUT /api/v1/regulation/{key}/ - Update regulation value (admin only)
    GET /api/v1/regulation/history/ - Get regulation change history (staff can read)
    """
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = []  # Will be set by get_permissions()
    
    def get_permissions(self):
        """
        Return different permissions based on HTTP method
        GET requests: Staff can read (ConfigReadPermission)
        POST/PUT requests: Admin only (ConfigPermission)
        """
        if self.request.method == 'GET':
            permission_classes = [ConfigReadPermission]
        else:
            permission_classes = [ConfigPermission]
        return [permission() for permission in permission_classes]
    
    def list(self, request):
        """List all regulations"""
        regulations = Regulation.objects.all()
        serializer = RegulationListSerializer(regulations, many=True)
        return Response(serializer.data)
    
    def create(self, request):
        """Create new regulation"""
        serializer = RegulationCreateSerializer(
            data=request.data,
            context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        regulation = serializer.save()
        
        # Return created regulation
        detail_serializer = RegulationDetailSerializer(regulation)
        return Response(detail_serializer.data, status=status.HTTP_201_CREATED)
    
    def retrieve(self, request, pk=None):
        """Get regulation by key"""
        regulation = get_object_or_404(Regulation, regulation_key=pk)
        serializer = RegulationDetailSerializer(regulation)
        return Response(serializer.data)
    
    def update(self, request, pk=None):
        """Update regulation value"""
        regulation = get_object_or_404(Regulation, regulation_key=pk)
        serializer = RegulationUpdateSerializer(
            regulation, 
            data=request.data, 
            context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        # Return updated regulation
        detail_serializer = RegulationDetailSerializer(regulation)
        return Response(detail_serializer.data)
    
    @action(detail=False, methods=["get"])
    def history(self, request):
        """Get regulation change history"""
        regulation_key = request.query_params.get("key")
        
        # Since we dont have a RegulationHistory model in DDL.sql,
        # we will return a simplified history based on updated_at
        history_data = []
        
        regulations_query = Regulation.objects.all()
        if regulation_key:
            regulations_query = regulations_query.filter(regulation_key=regulation_key)
        
        for regulation in regulations_query.order_by("-updated_at"):
            history_data.append({
                "regulation_key": regulation.regulation_key,
                "old_value": None,  # We dont track old values without history table
                "new_value": regulation.regulation_value,
                "changed_by": regulation.last_updated_by,
                "changed_by_name": self._get_user_name(regulation.last_updated_by),
                "changed_at": regulation.updated_at
            })
        
        serializer = RegulationHistorySerializer(history_data, many=True)
        return Response(serializer.data)
    
    def _get_user_name(self, user_id):
        """Helper method to get user name"""
        if user_id:
            try:
                from authentication.models import User
                user = User.objects.get(user_id=user_id)
                return user.full_name
            except User.DoesNotExist:
                return "Unknown User"
        return None
