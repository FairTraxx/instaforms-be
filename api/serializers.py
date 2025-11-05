from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Form, FormField, FormSubmission, FieldResponse


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']


class FormFieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = FormField
        fields = ['id', 'label', 'field_type', 'required', 'placeholder', 'options', 'order']


class FormSerializer(serializers.ModelSerializer):
    fields = FormFieldSerializer(many=True, read_only=True)
    created_by = UserSerializer(read_only=True)

    class Meta:
        model = Form
        fields = ['id', 'title', 'description', 'created_by', 'created_at', 'updated_at', 'is_active', 'fields']
        read_only_fields = ['created_at', 'updated_at']

    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class FieldResponseSerializer(serializers.ModelSerializer):
    field = FormFieldSerializer(read_only=True)
    field_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = FieldResponse
        fields = ['id', 'field', 'field_id', 'value']


class FormSubmissionSerializer(serializers.ModelSerializer):
    responses = FieldResponseSerializer(many=True)
    form = FormSerializer(read_only=True)

    class Meta:
        model = FormSubmission
        fields = ['id', 'form', 'submitted_at', 'responses']
        read_only_fields = ['submitted_at']

    def create(self, validated_data):
        responses_data = validated_data.pop('responses')
        submission = FormSubmission.objects.create(**validated_data)
        
        for response_data in responses_data:
            FieldResponse.objects.create(submission=submission, **response_data)
        
        return submission
