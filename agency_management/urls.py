"""
URL configuration for agency_management project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # Django Admin
    path("admin/", admin.site.urls),
    
    # API v1 endpoints per docs/api.md specification
    # Base URL: https://<domain>/api/v1/
    path("api/v1/", include([
        # Agency Management APIs (core functionality)
        path("", include("agency.urls")),
        
        # Authentication & User Management APIs
        path("", include("authentication.urls")),  # Includes auth/login, auth/me, users/
        
        # Inventory Management APIs (Items, Receipts, Issues)
        path("inventory/", include("inventory.urls")),      # /inventory/items/, /inventory/receipts/, /inventory/issues/
        
        # Finance Management APIs (Payments, Reports, Debts)
        path("finance/", include("finance.urls")),        # /finance/payments/, /finance/reports/, /finance/debts/
        
        # System Configuration APIs
        path("", include("regulation.urls")),     # /regulation/
    ])),
]

"""
Complete API URL Structure (following docs/api.md):

=== AUTHENTICATION & USER MANAGEMENT ===
POST         /api/v1/auth/login/           # Login (email + password) → set tokens
POST         /api/v1/auth/refresh/         # Exchange refresh → new access token  
POST         /api/v1/auth/logout/          # Invalidate current refresh token
GET          /api/v1/auth/me/              # Current user profile
PUT          /api/v1/auth/change-password/ # Self-service password change
GET/POST     /api/v1/users/                # List/create users (admin)
GET/PUT/PATCH/DELETE /api/v1/users/{id}/   # User CRUD operations

=== AGENCY MANAGEMENT ===
# Agency Types
GET/POST     /api/v1/agency-types/
GET/PUT/PATCH/DELETE /api/v1/agency-types/{id}/

# Districts  
GET/POST     /api/v1/districts/
GET/PUT/PATCH/DELETE /api/v1/districts/{id}/
GET          /api/v1/districts/{id}/capacity/

# Agencies (Core)
GET/POST     /api/v1/agency/
GET/PUT/PATCH/DELETE /api/v1/agency/{id}/
POST         /api/v1/agency/{id}/approve/
POST         /api/v1/agency/{id}/block/
GET          /api/v1/agency/{id}/debt/
GET          /api/v1/agency/{id}/history/

# Staff-Agency Relationships
GET/POST     /api/v1/staff-agency/
GET/DELETE   /api/v1/staff-agency/{composite_pk}/
GET          /api/v1/staff-agency/by_staff/?staff_id={id}
GET          /api/v1/staff-agency/by_agency/?agency_id={id}

=== INVENTORY MANAGEMENT ===
# Units
GET/POST     /api/v1/inventory/units/
GET/PUT/PATCH/DELETE /api/v1/inventory/units/{id}/

# Items
GET/POST     /api/v1/inventory/items/      # List/create items + search (?q=bolt)
GET/PUT/PATCH/DELETE /api/v1/inventory/items/{id}/ # Item CRUD
GET          /api/v1/inventory/items/low_stock/ # Items with low stock

# Receipts (Stock-in)
GET/POST     /api/v1/inventory/receipts/   # List/create receipts + filters (?agency_id=&date__gte=)
GET          /api/v1/inventory/receipts/{id}/ # Receipt details with nested items

# Issues (Stock-out)  
GET/POST     /api/v1/inventory/issues/     # List/create issues + filters (?agency_id=&date=)
GET          /api/v1/inventory/issues/{id}/ # Issue details with debt impact
GET          /api/v1/inventory/issues/by_agency/?agency_id={id} # Issues for specific agency

=== FINANCE MANAGEMENT ===
# Payments
GET/POST     /api/v1/finance/payments/     # List/create payments + filters (?agency_id=&date__range=)
GET          /api/v1/finance/payments/{id}/ # Payment details with debt impact

# Reports
GET/POST     /api/v1/finance/reports/      # List/create reports
GET          /api/v1/finance/reports/{id}/ # Report details

# Debt Management
GET          /api/v1/finance/debts/        # All debt transactions + filters (?agency_id=)
GET          /api/v1/finance/debts/summary/ # Debt summary by agency (?agency_id=)
GET          /api/v1/finance/debts/aging/  # Debt aging buckets analysis (?agency_id=)

=== SYSTEM CONFIGURATION ===
GET          /api/v1/regulation/           # List all regulation keys
GET/PUT      /api/v1/regulation/{key}/     # Get/update specific regulation value
GET          /api/v1/regulation/history/   # Configuration change log (?key=)

=== GLOBAL API CONVENTIONS ===

Authentication:
- All endpoints require JWT token (except /auth/login, /auth/refresh)
- Token via Authorization: Bearer {token} OR HttpOnly cookie

Pagination:
- ?limit={20}&offset={40} for all list endpoints
- Response: {"count": N, "next": "...", "previous": "...", "results": [...]}

Filtering & Search:
- ?search={query} for text search
- ?{field}={value} for exact filtering  
- ?ordering={field} or ?ordering=-{field} for sorting

Error Handling:
- 400: {"error": "Validation error", "details": {...}}
- 401: {"error": "Authentication required"}  
- 403: {"error": "Permission denied"}
- 404: {"error": "Resource not found"}
- 409: {"error": "BUSINESS_RULE", "code": "DEBT_LIMIT", "details": {...}}

Business Rules:
- DEBT_LIMIT: Issue would exceed agency debt limit
- OUT_OF_STOCK: Item quantity insufficient for issue
- INVALID_TOKEN: Access JWT expired or malformed
- PERMISSION_DENIED: JWT valid but missing required scope

WebSocket Notifications (future):
- wss://<domain>/ws/notify/ for real-time updates
"""
