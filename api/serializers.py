"""
Serializers for the InstaForms API.

This module contains all serializers for handling data validation and 
serialization/deserialization for the InstaForms application.
"""

from rest_framework import serializers
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from .models import Form, FormField, FormSubmission, FieldResponse


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User model.
    
    Provides read-only representation of user data for use in other serializers
    and views. Excludes sensitive information like passwords.
    """
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
        read_only_fields = ['id']


class RegisterSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.
    
    Handles user registration with password validation and confirmation.
    Uses email as the primary identifier. Username is auto-generated from email.
    Creates both the user and their authentication token upon successful registration.
    
    Fields:
        email: Valid email address (required, used for login)
        password: Password that meets Django's validation requirements
        password2: Password confirmation field (must match password)
    
    Note:
        First name and last name can be added later via the profile update endpoint.
    """
    
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'},
        help_text="Password must meet security requirements"
    )
    password2 = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        help_text="Confirm your password"
    )
    email = serializers.EmailField(
        required=True,
        help_text="Valid email address"
    )
    
    class Meta:
        model = User
        fields = ['email', 'password', 'password2']
    
    def validate_email(self, value):
        """
        Validate that the email is unique.
        
        Args:
            value: The email address to validate
            
        Returns:
            The validated email address
            
        Raises:
            serializers.ValidationError: If email already exists
        """
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value
    
    def validate(self, attrs):
        """
        Validate that passwords match.
        
        Args:
            attrs: Dictionary of all field values
            
        Returns:
            Validated attributes
            
        Raises:
            serializers.ValidationError: If passwords don't match
        """
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({
                "password": "Password fields didn't match."
            })
        return attrs
    
    def create(self, validated_data):
        """
        Create a new user with encrypted password.
        Username is auto-generated from email address.
        
        Args:
            validated_data: Validated user data
            
        Returns:
            Newly created User instance
        """
        # Remove password2 as it's not part of the User model
        validated_data.pop('password2')
        
        email = validated_data['email']
        
        # Generate username from email (use part before @ and add random suffix if needed)
        base_username = email.split('@')[0].lower()
        username = base_username
        
        # Ensure username is unique by adding a counter if necessary
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{base_username}{counter}"
            counter += 1
        
        # Create user with encrypted password
        user = User.objects.create_user(
            username=username,
            email=email,
            password=validated_data['password']
        )
        
        # Create auth token for the user
        Token.objects.create(user=user)
        
        return user


class LoginSerializer(serializers.Serializer):
    """
    Serializer for user login.
    
    Validates user credentials and returns user data with authentication token.
    Uses email and password for authentication.
    
    Fields:
        email: Email address
        password: User's password
    """
    
    email = serializers.EmailField(
        required=True,
        help_text="Email address"
    )
    password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'},
        help_text="User password"
    )
    
    def validate(self, attrs):
        """
        Validate user credentials using email and password.
        
        Args:
            attrs: Dictionary containing email and password
            
        Returns:
            Validated attributes with user object
            
        Raises:
            serializers.ValidationError: If credentials are invalid
        """
        from django.contrib.auth import authenticate
        
        email = attrs.get('email')
        password = attrs.get('password')
        
        # Get user by email and authenticate
        try:
            user_obj = User.objects.get(email=email)
            user = authenticate(username=user_obj.username, password=password)
        except User.DoesNotExist:
            user = None
        
        if not user:
            raise serializers.ValidationError(
                "Unable to log in with provided credentials.",
                code='authentication'
            )
        
        if not user.is_active:
            raise serializers.ValidationError(
                "User account is disabled.",
                code='authentication'
            )
        
        attrs['user'] = user
        return attrs


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for user profile updates.
    
    Allows users to update their profile information.
    Password updates are handled separately for security.
    
    Fields:
        username: Read-only username
        email: User's email address
        first_name: User's first name
        last_name: User's last name
    """
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'date_joined']
        read_only_fields = ['id', 'username', 'date_joined']
    
    def validate_email(self, value):
        """
        Validate that the email is unique (excluding current user).
        
        Args:
            value: The email address to validate
            
        Returns:
            The validated email address
            
        Raises:
            serializers.ValidationError: If email already exists for another user
        """
        user = self.context['request'].user
        if User.objects.filter(email=value).exclude(pk=user.pk).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value


class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer for password change.
    
    Validates current password and updates to new password.
    
    Fields:
        old_password: Current password for verification
        new_password: New password that meets validation requirements
        new_password2: Confirmation of new password
    """
    
    old_password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'},
        help_text="Current password"
    )
    new_password = serializers.CharField(
        required=True,
        write_only=True,
        validators=[validate_password],
        style={'input_type': 'password'},
        help_text="New password"
    )
    new_password2 = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'},
        help_text="Confirm new password"
    )
    
    def validate_old_password(self, value):
        """
        Validate that the old password is correct.
        
        Args:
            value: The old password to validate
            
        Returns:
            The validated password
            
        Raises:
            serializers.ValidationError: If old password is incorrect
        """
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect.")
        return value
    
    def validate(self, attrs):
        """
        Validate that new passwords match.
        
        Args:
            attrs: Dictionary of all field values
            
        Returns:
            Validated attributes
            
        Raises:
            serializers.ValidationError: If new passwords don't match
        """
        if attrs['new_password'] != attrs['new_password2']:
            raise serializers.ValidationError({
                "new_password": "New password fields didn't match."
            })
        return attrs
    
    def save(self, **kwargs):
        """
        Update the user's password.
        
        Returns:
            Updated User instance
        """
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user


class FormFieldSerializer(serializers.ModelSerializer):
    """
    Serializer for FormField model.
    
    Handles serialization of form field configuration including field type,
    validation rules, and display options.
    
    Fields:
        id: Unique identifier for the field
        label: Display label for the field
        field_type: Type of field (text, email, number, etc.)
        required: Whether the field is mandatory
        placeholder: Placeholder text for the field
        options: JSON data for select/radio/checkbox options
        order: Display order of the field in the form
    """
    
    class Meta:
        model = FormField
        fields = ['id', 'label', 'field_type', 'required', 'placeholder', 'options', 'order']


class FormSerializer(serializers.ModelSerializer):
    """
    Serializer for Form model.
    
    Handles form creation and retrieval with nested field definitions.
    Automatically associates forms with the creating user.
    
    Fields:
        id: Unique identifier for the form
        title: Form title
        description: Optional form description
        created_by: User who created the form (read-only)
        created_at: Timestamp of form creation (read-only)
        updated_at: Timestamp of last update (read-only)
        is_active: Whether the form is active and accepting submissions
        fields: Nested list of form fields (read-only)
    """
    
    fields = FormFieldSerializer(many=True, read_only=True)
    created_by = UserSerializer(read_only=True)

    class Meta:
        model = Form
        fields = ['id', 'title', 'description', 'created_by', 'created_at', 'updated_at', 'is_active', 'fields']
        read_only_fields = ['created_at', 'updated_at']

    def create(self, validated_data):
        """
        Create a new form associated with the current user.
        
        Args:
            validated_data: Validated form data
            
        Returns:
            Newly created Form instance
        """
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class FieldResponseSerializer(serializers.ModelSerializer):
    """
    Serializer for FieldResponse model.
    
    Handles individual field responses within a form submission.
    
    Fields:
        id: Unique identifier for the response
        field: FormField object (read-only, for display)
        field_id: ID of the field being responded to (write-only)
        value: The response value as text
    """
    
    field = FormFieldSerializer(read_only=True)
    field_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = FieldResponse
        fields = ['id', 'field', 'field_id', 'value']


class FormSubmissionSerializer(serializers.ModelSerializer):
    """
    Serializer for FormSubmission model.
    
    Handles complete form submissions with nested field responses.
    Creates submission records with associated field responses in a single transaction.
    
    Fields:
        id: Unique identifier for the submission
        form: Form object (read-only)
        submitted_at: Timestamp of submission (read-only)
        responses: List of field responses (nested)
    """
    
    responses = FieldResponseSerializer(many=True)
    form = FormSerializer(read_only=True)

    class Meta:
        model = FormSubmission
        fields = ['id', 'form', 'submitted_at', 'responses']
        read_only_fields = ['submitted_at']

    def create(self, validated_data):
        """
        Create a form submission with associated field responses.
        
        Args:
            validated_data: Validated submission data including responses
            
        Returns:
            Newly created FormSubmission instance with responses
        """
        responses_data = validated_data.pop('responses')
        submission = FormSubmission.objects.create(**validated_data)
        
        for response_data in responses_data:
            FieldResponse.objects.create(submission=submission, **response_data)
        
        return submission
