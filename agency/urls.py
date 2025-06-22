from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AgencyTypeViewSet, DistrictViewSet, AgencyViewSet, StaffAgencyViewSet

# Create router and register viewsets per docs/api.md patterns
router = DefaultRouter()

# Agency Type management (/api/v1/agency-types/)
router.register(r'agency-types', AgencyTypeViewSet, basename='agencytype')

# District management (/api/v1/districts/)  
router.register(r'districts', DistrictViewSet, basename='district')

# Main Agency management (/api/v1/agency/) - core endpoints per docs/api.md
router.register(r'agency', AgencyViewSet, basename='agency')

# Staff-Agency relationship management (/api/v1/staff-agency/)
router.register(r'staff-agency', StaffAgencyViewSet, basename='staffagency')

app_name = 'agency'

urlpatterns = [
    path('', include(router.urls)),
]

"""
Generated URL Patterns (per docs/api.md specification):

=== Agency Type Management ===
GET     /api/v1/agency-types/                    # List all agency types
POST    /api/v1/agency-types/                    # Create new agency type
GET     /api/v1/agency-types/{id}/               # Get agency type details
PUT     /api/v1/agency-types/{id}/               # Update agency type
PATCH   /api/v1/agency-types/{id}/               # Partial update agency type
DELETE  /api/v1/agency-types/{id}/               # Delete agency type

Query params: ?search={type_name}&ordering={field}

=== District Management ===
GET     /api/v1/districts/                       # List all districts
POST    /api/v1/districts/                       # Create new district
GET     /api/v1/districts/{id}/                  # Get district details
PUT     /api/v1/districts/{id}/                  # Update district
PATCH   /api/v1/districts/{id}/                  # Partial update district
DELETE  /api/v1/districts/{id}/                  # Delete district
GET     /api/v1/districts/{id}/capacity/         # Get district capacity info

Query params: ?city_name={city}&search={district_name}&ordering={field}

=== Agency Management (Core) ===
GET     /api/v1/agency/                          # List agencies (AgencyListSerializer)
POST    /api/v1/agency/                          # Register new agency (AgencyCreateSerializer)
GET     /api/v1/agency/{id}/                     # Get agency details (AgencyDetailSerializer)
PUT     /api/v1/agency/{id}/                     # Update agency
PATCH   /api/v1/agency/{id}/                     # Partial update agency
DELETE  /api/v1/agency/{id}/                     # Delete agency

# Custom actions per docs/flow.md business logic:
POST    /api/v1/agency/{id}/approve/             # Approve pending agency
POST    /api/v1/agency/{id}/block/               # Block/unblock agency operations
GET     /api/v1/agency/{id}/debt/                # Current debt & aging buckets
GET     /api/v1/agency/{id}/history/             # All receipts, issues, payments

Query params: 
- ?search={agency_name,email,phone_number,representative}
- ?agency_type={id}&district={id}&debt_amount={amount}
- ?ordering={agency_name,reception_date,debt_amount,created_at}
- ?status={PENDING,ACTIVE,BLOCKED} (future extension)

=== Staff-Agency Relationships ===
GET     /api/v1/staff-agency/                    # List all staff-agency relationships
POST    /api/v1/staff-agency/                    # Create staff-agency relationship
GET     /api/v1/staff-agency/{composite_pk}/     # Get relationship details (Note: composite PK)
DELETE  /api/v1/staff-agency/{composite_pk}/     # Remove staff-agency relationship

# Custom actions:
GET     /api/v1/staff-agency/by_staff/           # Get agencies by staff_id (?staff_id={id})
GET     /api/v1/staff-agency/by_agency/          # Get staff by agency_id (?agency_id={id})

Query params: ?staff_id={id}&agency={id}

=== Authentication Requirements ===
All endpoints require:
- Authorization: Bearer {access_token} OR
- HttpOnly Cookie: access={jwt_token}

=== Error Responses ===
400 Bad Request:     { "error": "Validation error", "details": {...} }
401 Unauthorized:    { "error": "Authentication required" }
403 Forbidden:       { "error": "Permission denied" }
404 Not Found:       { "error": "Resource not found" }
409 Conflict:        { "error": "DEBT_LIMIT", "max": 50000, "current": 49000 }

=== Pagination (all list endpoints) ===
Query params: ?limit={20}&offset={40}
Response: { "count": 100, "next": "...", "previous": "...", "results": [...] }

=== Example Usage ===

# Register new agency
POST /api/v1/agency/
{
    "agency_name": "Đại lý ABC",
    "phone_number": "0123456789", 
    "address": "123 Main St",
    "agency_type_id": 1,
    "district_id": 2,
    "reception_date": "2024-01-15"
}

# Get agency with debt info
GET /api/v1/agency/1/debt/
{
    "agency_id": 1,
    "current_debt": 25000.00,
    "max_debt": 50000.00,
    "debt_utilization": 50.0,
    "is_over_limit": false
}

# Search agencies
GET /api/v1/agency/?search=ABC&agency_type=1&ordering=-debt_amount

# Approve agency (admin action)
POST /api/v1/agency/1/approve/
{
    "message": "Agency approved successfully",
    "approved_at": "2024-01-15T10:30:00Z"
}
""" 