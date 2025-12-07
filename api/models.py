"""
Database Models for InstaForms.

This module defines all database models for the InstaForms application,
including forms, form fields, submissions, and field responses.
"""

from django.db import models
from django.contrib.auth.models import User


class Form(models.Model):
    """
    Model representing a form that can be filled out by users.
    
    A form is a collection of fields created by a user. Forms can be
    activated or deactivated to control public accessibility.
    
    Attributes:
        title (str): The title of the form (max 200 characters)
        description (str): Optional detailed description of the form's purpose
        created_by (User): Foreign key to the user who created the form
        created_at (datetime): Timestamp when the form was created
        updated_at (datetime): Timestamp when the form was last modified
        is_active (bool): Whether the form is active and accepting submissions
    
    Related Fields:
        fields: QuerySet of FormField objects belonging to this form
        submissions: QuerySet of FormSubmission objects for this form
    
    Meta:
        ordering: Forms are ordered by creation date (newest first)
    """
    
    title = models.CharField(
        max_length=200,
        help_text="Title of the form"
    )
    description = models.TextField(
        blank=True,
        help_text="Optional description of the form"
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        help_text="User who created this form"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when form was created"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp when form was last updated"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether the form is active and accepting submissions"
    )

    def __str__(self):
        """Return string representation of the form."""
        return self.title

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Form'
        verbose_name_plural = 'Forms'




class FormField(models.Model):
    """
    Model representing a field within a form.
    
    Form fields define the structure of data that can be collected through
    a form. Each field has a type (text, email, select, etc.) and validation rules.
    
    Attributes:
        form (Form): Foreign key to the parent form
        label (str): Display label for the field (max 200 characters)
        field_type (str): Type of input field (see FIELD_TYPES)
        required (bool): Whether this field must be filled out
        placeholder (str): Optional placeholder text for the input
        options (dict/list): JSON data for select/radio/checkbox options
        order (int): Display order of the field within the form
    
    Field Types:
        - text: Single-line text input
        - email: Email address input with validation
        - number: Numeric input
        - textarea: Multi-line text input
        - select: Dropdown selection
        - radio: Radio button selection
        - checkbox: Checkbox input
        - date: Date picker input
        - file: File upload input
    
    Related Fields:
        fieldresponse_set: QuerySet of responses to this field
    
    Meta:
        ordering: Fields are ordered by their 'order' attribute
    """
    
    FIELD_TYPES = [
        ('text', 'Text'),
        ('email', 'Email'),
        ('number', 'Number'),
        ('textarea', 'Textarea'),
        ('select', 'Select'),
        ('radio', 'Radio'),
        ('checkbox', 'Checkbox'),
        ('date', 'Date'),
        ('file', 'File'),
    ]

    form = models.ForeignKey(
        Form,
        on_delete=models.CASCADE,
        related_name='fields',
        help_text="Form this field belongs to"
    )
    label = models.CharField(
        max_length=200,
        help_text="Label displayed for this field"
    )
    field_type = models.CharField(
        max_length=20,
        choices=FIELD_TYPES,
        help_text="Type of input field"
    )
    required = models.BooleanField(
        default=False,
        help_text="Whether this field is required"
    )
    placeholder = models.CharField(
        max_length=200,
        blank=True,
        help_text="Placeholder text for the input"
    )
    options = models.JSONField(
        blank=True,
        null=True,
        help_text="Options for select, radio, or checkbox fields"
    )
    order = models.PositiveIntegerField(
        default=0,
        help_text="Display order of the field"
    )

    def __str__(self):
        """Return string representation of the field."""
        return f"{self.form.title} - {self.label}"

    class Meta:
        ordering = ['order']
        verbose_name = 'Form Field'
        verbose_name_plural = 'Form Fields'


class FormSubmission(models.Model):
    """
    Model representing a submission to a form.
    
    A form submission is a collection of field responses submitted by a user.
    Each submission is timestamped and optionally stores the submitter's IP address.
    
    Attributes:
        form (Form): Foreign key to the form being submitted
        submitted_at (datetime): Timestamp when the submission was created
        ip_address (str): IP address of the submitter (optional, for analytics)
    
    Related Fields:
        responses: QuerySet of FieldResponse objects for this submission
    
    Meta:
        ordering: Submissions are ordered by submission date (newest first)
    """
    
    form = models.ForeignKey(
        Form,
        on_delete=models.CASCADE,
        related_name='submissions',
        help_text="Form this submission belongs to"
    )
    submitted_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when submission was created"
    )
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        help_text="IP address of the submitter"
    )

    def __str__(self):
        """Return string representation of the submission."""
        return f"Submission for {self.form.title} at {self.submitted_at}"

    class Meta:
        ordering = ['-submitted_at']
        verbose_name = 'Form Submission'
        verbose_name_plural = 'Form Submissions'


class FieldResponse(models.Model):
    """
    Model representing a response to a specific field in a form submission.
    
    Each field response stores the value submitted for a particular field
    within a form submission. All values are stored as text and can be
    parsed based on the field type.
    
    Attributes:
        submission (FormSubmission): Foreign key to the parent submission
        field (FormField): Foreign key to the field being responded to
        value (str): The response value as text
    
    Meta:
        No specific ordering (ordering handled by related FormField.order)
    """
    
    submission = models.ForeignKey(
        FormSubmission,
        on_delete=models.CASCADE,
        related_name='responses',
        help_text="Submission this response belongs to"
    )
    field = models.ForeignKey(
        FormField,
        on_delete=models.CASCADE,
        help_text="Field this response is for"
    )
    value = models.TextField(
        help_text="The response value"
    )

    def __str__(self):
        """Return string representation of the response."""
        return f"{self.field.label}: {self.value}"

    class Meta:
        verbose_name = 'Field Response'
        verbose_name_plural = 'Field Responses'
