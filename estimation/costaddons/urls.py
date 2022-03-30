from django.urls import path
from estimation.costaddons import views

urlpatterns = [
    path('api/costaddons/config', 
        views.ConfigCostAddonViewSet.as_view({'get': 'list', 'post': 'create'})),
    path('api/costaddons/config/<pk>/',
        views.ConfigCostAddonViewSet.as_view({'get': 'retrieve', 'put': 'update',
            'delete': 'destroy'})),

    path('api/costaddons/template',
        views.TemplateCostAddonSetSerializerViewSet.as_view({'get': 'list', 'post': 'create'})),
    path('api/costaddons/template/<pk>/',
        views.TemplateCostAddonSetSerializerViewSet.as_view({'get': 'retrieve', 'put': 'update',
            'delete': 'destroy'})),
]