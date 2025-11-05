from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from .models import Form, FormField, FormSubmission


class FormAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)

    def test_create_form(self):
        """Test creating a new form"""
        data = {
            'title': 'Test Form',
            'description': 'A test form',
            'is_active': True
        }
        response = self.client.post('/api/forms/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Form.objects.count(), 1)
        self.assertEqual(Form.objects.first().title, 'Test Form')

    def test_list_forms(self):
        """Test listing user's forms"""
        Form.objects.create(
            title='Test Form',
            description='A test form',
            created_by=self.user
        )
        response = self.client.get('/api/forms/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_add_field_to_form(self):
        """Test adding a field to a form"""
        form = Form.objects.create(
            title='Test Form',
            description='A test form',
            created_by=self.user
        )
        data = {
            'label': 'Name',
            'field_type': 'text',
            'required': True,
            'order': 1
        }
        response = self.client.post(f'/api/forms/{form.id}/add_field/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(FormField.objects.count(), 1)


class PublicFormAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.form = Form.objects.create(
            title='Public Form',
            description='A public test form',
            created_by=self.user,
            is_active=True
        )
        self.field = FormField.objects.create(
            form=self.form,
            label='Name',
            field_type='text',
            required=True,
            order=1
        )

    def test_list_public_forms(self):
        """Test listing public forms without authentication"""
        response = self.client.get('/api/public/forms/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_submit_form(self):
        """Test submitting a form response"""
        data = {
            'responses': [
                {
                    'field_id': self.field.id,
                    'value': 'John Doe'
                }
            ]
        }
        response = self.client.post(f'/api/public/forms/{self.form.id}/submit/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(FormSubmission.objects.count(), 1)
