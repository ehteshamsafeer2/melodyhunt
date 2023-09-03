from django.urls import path
from . import views

urlpatterns = [
    path('home/', views.separate_instruments, name='separate_instruments'),
]

