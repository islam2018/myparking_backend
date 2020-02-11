from django.contrib import admin
from django.contrib.auth import get_user_model
from django.urls import path, include
from . import views
from rest_framework import routers
from rest_framework_simplejwt.views import TokenRefreshView

from .views import DriverLoginViewJWT, AgentLoginViewJWT

router = routers.DefaultRouter()
router.register('parking', views.ParkingView)
router.register('register/driver', views.RegistrationAutomobilisteView)
router.register('register/agent', views.RegistrationAgentView)

urlpatterns = [
    path('', include(router.urls)),
    # path('api-auth/', include('rest_framework.urls')),
    path('api/driver/login', DriverLoginViewJWT.as_view()),
    path('api/agent/login', AgentLoginViewJWT.as_view()),
    path('api/token/refresh', TokenRefreshView.as_view())
]
