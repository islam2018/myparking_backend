from django.contrib import admin
from django.contrib.auth import get_user_model
from django.urls import path, include
from . import views
from rest_framework import routers
from rest_framework_simplejwt.views import TokenRefreshView

from .views import UserLoginViewJWT

router = routers.DefaultRouter()
router.register('parking', views.ParkingView)
router.register('register', views.RegistrationView)

urlpatterns = [
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls')),
    path('api/token', UserLoginViewJWT.as_view()),
    path('api/token/refresh', TokenRefreshView.as_view())
]
