from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ValidationError
from django.db import IntegrityError


def custom_exception_handler(exc, context):
    """
    Custom exception handler that returns errors in the format specified by docs/api.md:
    {"code": "<ERR_CODE>", "message": "Human-readable", "details": {...}}
    """
    # Call REST framework's default exception handler first
    response = exception_handler(exc, context)
    
    if response is not None:
        # Standard DRF errors - reformat them
        custom_response_data = format_error_response(response.data, response.status_code)
        response.data = custom_response_data
        return response
    
    # Handle non-DRF exceptions
    if isinstance(exc, ValidationError):
        return Response(
            format_validation_error(exc),
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if isinstance(exc, IntegrityError):
        return Response(
            format_integrity_error(exc),
            status=status.HTTP_409_CONFLICT
        )
    
    if isinstance(exc, BusinessRuleViolation):
        return Response(
            format_business_error(exc),
            status=status.HTTP_409_CONFLICT
        )
    
    # Let Django handle other exceptions
    return None


def format_error_response(data, status_code):
    """Format DRF errors into standard envelope"""
    if status_code == 400:
        return {
            "code": "VALIDATION_ERROR",
            "message": "Request validation failed",
            "details": data
        }
    elif status_code == 401:
        return {
            "code": "INVALID_TOKEN", 
            "message": "Authentication required or token invalid",
            "details": data
        }
    elif status_code == 403:
        return {
            "code": "PERMISSION_DENIED",
            "message": "Insufficient permissions for this operation", 
            "details": data
        }
    elif status_code == 404:
        return {
            "code": "NOT_FOUND",
            "message": "Requested resource not found",
            "details": data
        }
    else:
        return {
            "code": "ERROR",
            "message": "An error occurred",
            "details": data
        }


def format_validation_error(exc):
    """Format Django ValidationError"""
    if hasattr(exc, 'message_dict'):
        details = exc.message_dict
    elif hasattr(exc, 'messages'):
        details = {"non_field_errors": exc.messages}
    else:
        details = {"error": str(exc)}
        
    return {
        "code": "VALIDATION_ERROR",
        "message": "Data validation failed",
        "details": details
    }


def format_integrity_error(exc):
    """Format database integrity errors"""
    error_msg = str(exc)
    
    if 'unique constraint' in error_msg.lower():
        return {
            "code": "DUPLICATE_ENTRY", 
            "message": "A record with this data already exists",
            "details": {"database_error": error_msg}
        }
    elif 'foreign key constraint' in error_msg.lower():
        return {
            "code": "INVALID_REFERENCE",
            "message": "Referenced record does not exist", 
            "details": {"database_error": error_msg}
        }
    else:
        return {
            "code": "DATABASE_ERROR",
            "message": "Database constraint violation",
            "details": {"database_error": error_msg}
        }


def format_business_error(exc):
    """Format business rule violations"""
    return {
        "code": exc.code,
        "message": exc.message,
        "details": getattr(exc, 'details', {})
    }


class BusinessRuleViolation(Exception):
    """Base exception for business rule violations per docs/api.md"""
    def __init__(self, code, message, details=None):
        self.code = code
        self.message = message
        self.details = details or {}
        super().__init__(message)


class DebtLimitExceeded(BusinessRuleViolation):
    """Exception for debt limit violations"""
    def __init__(self, current_debt, max_debt, additional_amount):
        details = {
            "current_debt": float(current_debt),
            "max_debt": float(max_debt),
            "additional_amount": float(additional_amount),
            "available_credit": float(max_debt - current_debt)
        }
        super().__init__(
            code="DEBT_LIMIT",
            message=f"Issue would exceed configured debt limit ({max_debt})",
            details=details
        )


class OutOfStock(BusinessRuleViolation):
    """Exception for insufficient stock"""
    def __init__(self, item_name, requested_qty, available_qty):
        details = {
            "item_name": item_name,
            "requested_quantity": requested_qty,
            "available_quantity": available_qty,
            "shortage": requested_qty - available_qty
        }
        super().__init__(
            code="OUT_OF_STOCK",
            message=f"Insufficient stock for {item_name}",
            details=details
        ) 