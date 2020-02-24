from django.contrib import admin
from django.contrib.auth import get_user_model
from django.urls import include, path
from . import views
from rest_framework import routers
from rest_framework_simplejwt.views import TokenRefreshView

from .views import DriverLoginViewJWT, AgentLoginViewJWT, AdminLoginViewJWT

router = routers.DefaultRouter()
router.register('parking', views.ParkingView)
router.register('register/driver', views.RegistrationAutomobilisteView)
router.register('register/agent', views.RegistrationAgentView)
router.register('filterInfos', views.FilterInfosView),
router.register('reservation', views.ReservationView)

urlpatterns = [
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls')),
    # path('parking/<idParking>', views.ParkingView.as_view({'get': 'getOneParking'}), name='OneParking'),
    path('filterParkings', views.ParkingView.as_view({'get': 'filterParkings'}), name='FilterParking'),
    path('search', views.SearchView.as_view()),
    path('test', views.TestView.as_view()),
    path('api/driver/login', DriverLoginViewJWT.as_view()),
    path('api/agent/login', AgentLoginViewJWT.as_view()),
    path('api/admin/login', AdminLoginViewJWT.as_view()),
    path('api/token/refresh', TokenRefreshView.as_view())
]

