from django.contrib import admin
from .models import Form, FormField, FormSubmission, FieldResponse


@admin.register(Form)
class FormAdmin(admin.ModelAdmin):
    list_display = ['title', 'created_by', 'created_at', 'is_active']
    list_filter = ['is_active', 'created_at']
    search_fields = ['title', 'description']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(FormField)
class FormFieldAdmin(admin.ModelAdmin):
    list_display = ['label', 'form', 'field_type', 'required', 'order']
    list_filter = ['field_type', 'required']
    search_fields = ['label', 'form__title']


@admin.register(FormSubmission)
class FormSubmissionAdmin(admin.ModelAdmin):
    list_display = ['form', 'submitted_at', 'ip_address']
    list_filter = ['submitted_at', 'form']
    readonly_fields = ['submitted_at']


@admin.register(FieldResponse)
class FieldResponseAdmin(admin.ModelAdmin):
    list_display = ['field', 'submission', 'value']
    list_filter = ['field__field_type']
    search_fields = ['value', 'field__label']
