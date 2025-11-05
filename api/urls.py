from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'forms', views.FormViewSet, basename='form')
router.register(r'fields', views.FormFieldViewSet, basename='formfield')
router.register(r'submissions', views.FormSubmissionViewSet, basename='submission')
router.register(r'public/forms', views.PublicFormViewSet, basename='public-form')

urlpatterns = [
    path('api/', include(router.urls)),
    path('api-auth/', include('rest_framework.urls')),
]
