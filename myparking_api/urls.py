import threading
from _thread import start_new_thread

from django.urls import include, path

from model_optim import runModel, AFTER_SERVER_INIT
from model_optim.forSimulationOnly import optimizeWithoutClustering
from model_optim.simulation import main_test_fun
from . import views
from rest_framework import routers
from rest_framework_simplejwt.views import TokenRefreshView

from .views import DriverLoginViewJWT, AgentLoginViewJWT, AdminLoginViewJWT

router = routers.DefaultRouter()
router.register('parking', views.ParkingView)
router.register('favoris', views.FavorisView)
router.register('register/driver', views.RegistrationAutomobilisteView)
router.register('register/agent', views.RegistrationAgentView)
router.register('filterInfos', views.FilterInfosView),
router.register('reservation', views.ReservationView)
router.register('equipements', views.EquipementView)
router.register('paiements', views.PaiementView)

urlpatterns = [
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls')),
    path('getParkings', views.TestParkingView.as_view({'get': 'withMode'}), name='withMode'),
    # path('filterParkings', views.ParkingView.as_view({'get': 'filterParkings'}), name='FilterParking'),
    path('search', views.SearchView.as_view()),
    path('api/driver/login', DriverLoginViewJWT.as_view()),
    path('api/agent/login', AgentLoginViewJWT.as_view()),
    path('api/admin/login', AdminLoginViewJWT.as_view()),
    path('api/token/refresh', TokenRefreshView.as_view()),
    path('reservation/qr/<code>', views.ReservationView.as_view({'get': 'checkQR'})),
    path('reservation/history', views.ReservationView.as_view({'get': 'history'})),
    path('reservation/validate/<id>', views.ReservationView.as_view({'post': 'validateQR'})),
    path('reservation/decline/<id>', views.ReservationView.as_view({'post': 'declineQR'})),
    path('favoris', views.FavorisView.as_view({'delete': 'delete'})),
    path('agent/report', views.SignalementView.as_view({'post': 'create'})),
    path('agent/<id>', views.AgentView.as_view()),
    path('driver/contact', views.ContactView.as_view({'post': 'create'})),
    path('driver/updateLocation', views.UpdateLocation.as_view({'post': 'updateDriverLocation'})),
    path('pusher/beams_auth/agent', views.BeamsAgentAuth.as_view()),
    path('pusher/beams_auth/driver', views.BeamsDriverAuth.as_view()),
    path('pusher/notify/agent', views.SendAgentNotif.as_view()),
    path('pusher/broadcast/agent', views.BroadcastAgent.as_view()),
    path('pusher/notify/driver', views.SendDriverNotif.as_view()),
    path('pusher/broadcast/driver', views.BroadcastDriver.as_view()),
    path('runTests/', views.TestParkingView.as_view({'get': 'runTests'})),

]

# Run the model after server is
#runModel() # hna 3edna a model (clusters are prepared in database)
optimizeWithoutClustering() #but here no so
# i can't do small number lol
# NU np WIN TNKSLHOM, mais f mode=1 it uses all ok
#AFTER_SERVER_INIT()

#main_test_fun()
