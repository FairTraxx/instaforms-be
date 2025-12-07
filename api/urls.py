"""
URL Configuration for InstaForms API.

This module defines all API endpoints for the InstaForms application.

API Structure:
    Authentication:
        POST   /api/auth/register/         - User registration
        POST   /api/auth/login/            - User login
        POST   /api/auth/logout/           - User logout
        GET    /api/auth/profile/          - Get user profile
        PATCH  /api/auth/profile/          - Update user profile
        POST   /api/auth/change-password/  - Change password
    
    Forms (Authenticated):
        GET    /api/forms/                 - List user's forms
        POST   /api/forms/                 - Create a new form
        GET    /api/forms/{id}/            - Get form details
        PUT    /api/forms/{id}/            - Update form
        PATCH  /api/forms/{id}/            - Partial update
        DELETE /api/forms/{id}/            - Delete form
        POST   /api/forms/{id}/add_field/  - Add field to form
        GET    /api/forms/{id}/submissions/ - Get form submissions
    
    Fields (Authenticated):
        GET    /api/fields/                - List user's form fields
        POST   /api/fields/                - Create a new field
        GET    /api/fields/{id}/           - Get field details
        PUT    /api/fields/{id}/           - Update field
        PATCH  /api/fields/{id}/           - Partial update
        DELETE /api/fields/{id}/           - Delete field
    
    Submissions (Authenticated):
        GET    /api/submissions/           - List user's form submissions
        GET    /api/submissions/{id}/      - Get submission details
    
    Public:
        GET    /api/public/forms/          - List active forms
        GET    /api/public/forms/{id}/     - Get form details
        POST   /api/public/forms/{id}/submit/ - Submit form response
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Initialize the router for ViewSets
router = DefaultRouter()
router.register(r'forms', views.FormViewSet, basename='form')
router.register(r'fields', views.FormFieldViewSet, basename='formfield')
router.register(r'submissions', views.FormSubmissionViewSet, basename='submission')
router.register(r'public/forms', views.PublicFormViewSet, basename='public-form')

# Define URL patterns
urlpatterns = [
    # Authentication endpoints
    path('api/auth/register/', views.RegisterView.as_view(), name='auth-register'),
    path('api/auth/login/', views.LoginView.as_view(), name='auth-login'),
    path('api/auth/logout/', views.LogoutView.as_view(), name='auth-logout'),
    path('api/auth/profile/', views.UserProfileView.as_view(), name='auth-profile'),
    path('api/auth/change-password/', views.ChangePasswordView.as_view(), name='auth-change-password'),
    
    # Include router URLs (forms, fields, submissions, public forms)
    path('api/', include(router.urls)),
    
    # Django REST Framework browsable API login
    path('api-auth/', include('rest_framework.urls')),
]
