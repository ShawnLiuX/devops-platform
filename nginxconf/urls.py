from django.urls import path
from . import views

urlpatterns = [
    path('<str:env>/', views.nginxconf),
]
