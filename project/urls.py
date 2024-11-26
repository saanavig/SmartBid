"""
URL configuration for project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from dashboard import views
from django.contrib.auth.views import LoginView
from django.views.generic import TemplateView
from project.views import CustomSignupView
from .views import homepage, profile, CustomSignupView
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('allauth.urls')),  # Includes allauth's URLs (signup, login, etc.)
    path('accounts/profile/', views.profile, name="profile"),  # Profile view
    path('', TemplateView.as_view(template_name='homepage.html')),    
    path('login/', LoginView.as_view(), name='login'),
    path('signup/', CustomSignupView.as_view(), name='signup'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/account/', views.account, name='account'),
    path('dashboard/viewbids/', views.viewbids, name='viewbids'),
    path('dashboard/requests/', views.requests, name='requests'),
    
]
