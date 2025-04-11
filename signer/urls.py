from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('download/<int:doc_id>/', views.download_document, name='download_document'),
]