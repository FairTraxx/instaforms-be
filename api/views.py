from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth.models import User
from .models import Form, FormField, FormSubmission, FieldResponse
from .serializers import (
    FormSerializer, FormFieldSerializer, FormSubmissionSerializer,
    FieldResponseSerializer, UserSerializer
)


class FormViewSet(viewsets.ModelViewSet):
    serializer_class = FormSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Form.objects.filter(created_by=self.request.user)

    @action(detail=True, methods=['post'])
    def add_field(self, request, pk=None):
        form = self.get_object()
        serializer = FormFieldSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(form=form)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def submissions(self, request, pk=None):
        form = self.get_object()
        submissions = FormSubmission.objects.filter(form=form)
        serializer = FormSubmissionSerializer(submissions, many=True)
        return Response(serializer.data)


class FormFieldViewSet(viewsets.ModelViewSet):
    serializer_class = FormFieldSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return FormField.objects.filter(form__created_by=self.request.user)


class PublicFormViewSet(viewsets.ReadOnlyModelViewSet):
    """Public endpoint for viewing and submitting forms"""
    serializer_class = FormSerializer
    permission_classes = [permissions.AllowAny]
    queryset = Form.objects.filter(is_active=True)

    @action(detail=True, methods=['post'], permission_classes=[permissions.AllowAny])
    def submit(self, request, pk=None):
        form = self.get_object()
        
        # Get client IP
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')

        # Create submission
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
    serializer_class = FormSubmissionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return FormSubmission.objects.filter(form__created_by=self.request.user)
