from django.urls import path
from estimation import views

urlpatterns = [
    path('api/workstations', 
        views.WorkstationViewSet.as_view({'get': 'list', 'post':'create'})),
    path('api/workstations/<int:pk>/',
        views.WorkstationViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'})),
    path('api/workstations/<int:pk>/activities',
        views.WorkstationActivitiesViewSet.as_view({'get': 'list', 'post': 'create'}))
]