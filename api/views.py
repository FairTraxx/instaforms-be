"""
API Views for InstaForms.

This module contains all API views and viewsets for the InstaForms application,
including authentication endpoints, form management, and submission handling.
"""

from rest_framework import viewsets, status, permissions, generics
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from django.contrib.auth import logout
from .models import Form, FormField, FormSubmission, FieldResponse
from .serializers import (
    FormSerializer, FormFieldSerializer, FormSubmissionSerializer,
    FieldResponseSerializer, UserSerializer, RegisterSerializer,
    LoginSerializer, UserProfileSerializer, ChangePasswordSerializer
)


# ============================================================================
# Authentication Views
# ============================================================================

class RegisterView(generics.CreateAPIView):
    """
    API endpoint for user registration.
    
    POST /api/auth/register/
    
    Creates a new user account using email and password only.
    Username is auto-generated from the email address.
    Returns user data with authentication token.
    
    Request Body:
        {
            "email": "string (required, unique, valid email)",
            "password": "string (required, must meet security requirements)",
            "password2": "string (required, must match password)"
        }
    
    Response (201 Created):
        {
            "user": {
                "id": 1,
                "username": "john",
                "email": "john@example.com",
                "first_name": "",
                "last_name": ""
            },
            "token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b",
            "message": "User registered successfully"
        }
    
    Error Response (400 Bad Request):
        {
            "email": ["A user with this email already exists."],
            "password": ["This password is too common."]
        }
    
    Note:
        First name and last name can be added later via PATCH /api/auth/profile/
    """
    
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]
    
    def create(self, request, *args, **kwargs):
        """
        Handle user registration.
        
        Creates a new user and returns user data with authentication token.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Get or create token for the user
        token, created = Token.objects.get_or_create(user=user)
        
        return Response({
            'user': UserSerializer(user).data,
            'token': token.key,
            'message': 'User registered successfully'
        }, status=status.HTTP_201_CREATED)


class LoginView(generics.GenericAPIView):
    """
    API endpoint for user authentication.
    
    POST /api/auth/login/
    
    Authenticates user with email and password, returns authentication token.
    
    Request Body:
        {
            "email": "string (required, email address)",
            "password": "string (required)"
        }
    
    Response (200 OK):
        {
            "user": {
                "id": 1,
                "username": "john",
                "email": "john@example.com",
                "first_name": "John",
                "last_name": "Doe"
            },
            "token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b",
            "message": "Login successful"
        }
    
    Error Response (400 Bad Request):
        {
            "non_field_errors": ["Unable to log in with provided credentials."]
        }
    """
    
    serializer_class = LoginSerializer
    permission_classes = [permissions.AllowAny]
    
    def post(self, request, *args, **kwargs):
        """
        Handle user login.
        
        Validates credentials and returns user data with authentication token.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = serializer.validated_data['user']
        
        # Get or create token for the user
        token, created = Token.objects.get_or_create(user=user)
        
        return Response({
            'user': UserSerializer(user).data,
            'token': token.key,
            'message': 'Login successful'
        }, status=status.HTTP_200_OK)


class LogoutView(generics.GenericAPIView):
    """
    API endpoint for user logout.
    
    POST /api/auth/logout/
    
    Logs out the current user by deleting their authentication token.
    Requires authentication.
    
    Headers:
        Authorization: Token <token_key>
    
    Response (200 OK):
        {
            "message": "Logged out successfully"
        }
    
    Error Response (401 Unauthorized):
        {
            "detail": "Authentication credentials were not provided."
        }
    """
    
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        """
        Handle user logout.
        
        Deletes the user's authentication token.
        """
        try:
            # Delete the user's token to logout
            request.user.auth_token.delete()
            return Response({
                'message': 'Logged out successfully'
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                'error': 'Something went wrong'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    API endpoint for user profile management.
    
    GET /api/auth/profile/
    Retrieve the current user's profile information.
    
    PUT/PATCH /api/auth/profile/
    Update the current user's profile information.
    
    Headers:
        Authorization: Token <token_key>
    
    Response (200 OK):
        {
            "id": 1,
            "username": "john_doe",
            "email": "john@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "date_joined": "2024-01-01T00:00:00Z"
        }
    
    Update Request Body (PATCH):
        {
            "email": "newemail@example.com",
            "first_name": "Jonathan",
            "last_name": "Doe"
        }
    
    Note: Username cannot be updated. Use change-password endpoint for password changes.
    """
    
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        """
        Return the current authenticated user.
        """
        return self.request.user


class ChangePasswordView(generics.GenericAPIView):
    """
    API endpoint for changing user password.
    
    POST /api/auth/change-password/
    
    Allows authenticated users to change their password.
    Requires current password verification.
    
    Headers:
        Authorization: Token <token_key>
    
    Request Body:
        {
            "old_password": "string (required)",
            "new_password": "string (required, must meet security requirements)",
            "new_password2": "string (required, must match new_password)"
        }
    
    Response (200 OK):
        {
            "message": "Password changed successfully"
        }
    
    Error Response (400 Bad Request):
        {
            "old_password": ["Old password is incorrect."],
            "new_password": ["New password fields didn't match."]
        }
    """
    
    serializer_class = ChangePasswordSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        """
        Handle password change.
        
        Validates old password and updates to new password.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response({
            'message': 'Password changed successfully'
        }, status=status.HTTP_200_OK)


# ============================================================================
# Form Management Views
# ============================================================================

class FormViewSet(viewsets.ModelViewSet):
    """
    API ViewSet for managing forms.
    
    Provides CRUD operations for forms. Users can only access their own forms.
    
    Endpoints:
        GET    /api/forms/              - List all forms for authenticated user
        POST   /api/forms/              - Create a new form
        GET    /api/forms/{id}/         - Retrieve a specific form
        PUT    /api/forms/{id}/         - Update a form
        PATCH  /api/forms/{id}/         - Partially update a form
        DELETE /api/forms/{id}/         - Delete a form
        POST   /api/forms/{id}/add_field/ - Add a field to the form
        GET    /api/forms/{id}/submissions/ - Get all submissions for the form
    
    Permissions:
        - Requires authentication
        - Users can only access/modify their own forms
    """
    
    serializer_class = FormSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Filter forms to only show forms created by the current user.
        
        Returns:
            QuerySet of Form objects created by the authenticated user
        """
        return Form.objects.filter(created_by=self.request.user)

    @action(detail=True, methods=['post'])
    def add_field(self, request, pk=None):
        """
        Add a field to an existing form.
        
        POST /api/forms/{id}/add_field/
        
        Request Body:
            {
                "label": "string (required)",
                "field_type": "string (required, one of: text, email, number, etc.)",
                "required": "boolean (optional, default: false)",
                "placeholder": "string (optional)",
                "options": "object (optional, for select/radio/checkbox)",
                "order": "integer (optional, default: 0)"
            }
        
        Response (201 Created):
            Returns the created field data
        
        Error Response (400 Bad Request):
            Returns validation errors
        """
        form = self.get_object()
        serializer = FormFieldSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(form=form)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def submissions(self, request, pk=None):
        """
        Retrieve all submissions for a specific form.
        
        GET /api/forms/{id}/submissions/
        
        Returns a list of all submissions with their responses for the specified form.
        
        Response (200 OK):
            [
                {
                    "id": 1,
                    "form": {...},
                    "submitted_at": "2024-01-01T00:00:00Z",
                    "responses": [...]
                }
            ]
        """
        form = self.get_object()
        submissions = FormSubmission.objects.filter(form=form)
        serializer = FormSubmissionSerializer(submissions, many=True)
        return Response(serializer.data)


class FormFieldViewSet(viewsets.ModelViewSet):
    """
    API ViewSet for managing form fields.
    
    Provides CRUD operations for form fields. Users can only access fields
    from forms they created.
    
    Endpoints:
        GET    /api/fields/              - List all fields from user's forms
        POST   /api/fields/              - Create a new field
        GET    /api/fields/{id}/         - Retrieve a specific field
        PUT    /api/fields/{id}/         - Update a field
        PATCH  /api/fields/{id}/         - Partially update a field
        DELETE /api/fields/{id}/         - Delete a field
    
    Permissions:
        - Requires authentication
        - Users can only access/modify fields from their own forms
    """
    
    serializer_class = FormFieldSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Filter fields to only show fields from forms created by the current user.
        
        Returns:
            QuerySet of FormField objects from user's forms
        """
        return FormField.objects.filter(form__created_by=self.request.user)


class PublicFormViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Public API ViewSet for viewing and submitting forms.
    
    Provides read-only access to active forms and allows anonymous form submissions.
    No authentication required.
    
    Endpoints:
        GET  /api/public/forms/            - List all active forms
        GET  /api/public/forms/{id}/       - Retrieve a specific form with fields
        POST /api/public/forms/{id}/submit/ - Submit a response to the form
    
    Permissions:
        - No authentication required
        - Only active forms (is_active=True) are visible
    """
    
    serializer_class = FormSerializer
    permission_classes = [permissions.AllowAny]
    queryset = Form.objects.filter(is_active=True)

    @action(detail=True, methods=['post'], permission_classes=[permissions.AllowAny])
    def submit(self, request, pk=None):
        """
        Submit a response to a public form.
        
        POST /api/public/forms/{id}/submit/
        
        Captures the submitter's IP address and validates all field responses.
        
        Request Body:
            {
                "responses": [
                    {
                        "field_id": 1,
                        "value": "User's response"
                    },
                    {
                        "field_id": 2,
                        "value": "Another response"
                    }
                ]
            }
        
        Response (201 Created):
            {
                "message": "Form submitted successfully"
            }
        
        Error Response (400 Bad Request):
            Returns validation errors if required fields are missing
            or if field IDs are invalid
        """
        form = self.get_object()
        
        # Get client IP address
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')

        # Create submission with responses
        submission_data = {
            'form': form.id,
            'ip_address': ip,
            'responses': request.data.get('responses', [])
        }
        
        serializer = FormSubmissionSerializer(data=submission_data)
        if serializer.is_valid():
            serializer.save(form=form)
            return Response({'message': 'Form submitted successfully'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FormSubmissionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API ViewSet for viewing form submissions.
    
    Provides read-only access to form submissions. Users can only view
    submissions for forms they created.
    
    Endpoints:
        GET /api/submissions/     - List all submissions for user's forms
        GET /api/submissions/{id}/ - Retrieve a specific submission with responses
    
    Permissions:
        - Requires authentication
        - Users can only view submissions for their own forms
    """
    
    serializer_class = FormSubmissionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Filter submissions to only show submissions for user's forms.
        
        Returns:
            QuerySet of FormSubmission objects for forms created by the user
        """
        return FormSubmission.objects.filter(form__created_by=self.request.user)
