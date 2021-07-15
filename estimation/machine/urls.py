from django.urls import path
from estimation import views

urlpatterns = [
    # Machine Viewsets
    path('api/machines/types', views.MachineTypesViewSet.as_view({'get': 'list'})),
    path('api/machines/press', 
        views.SheetFedPressMachineViewSet.as_view({'get': 'list', 'post': 'create'})),
]