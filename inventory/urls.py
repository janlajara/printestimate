from django.urls import path
from inventory import views

GETLIST_POSTCREATE = {'get': 'list', 'post': 'create'}
GETRETRIEVE_PUTUPDATE_POSTDESTROY = {'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}

urlpatterns = [
    path('api/item',
         views.ItemViewSet.as_view(GETLIST_POSTCREATE)),
    path('api/item/<int:pk>/',
         views.ItemViewSet.as_view(GETRETRIEVE_PUTUPDATE_POSTDESTROY)),
    path('api/itemproperties',
         views.ItemPropertiesListCreateSerializer.as_view(GETLIST_POSTCREATE)),
    path('api/itemproperties/<int:pk>/',
         views.ItemPropertiesViewSet.as_view(GETRETRIEVE_PUTUPDATE_POSTDESTROY)),
    path('api/basestockunit',
         views.BaseStockUnitViewSet.as_view(GETLIST_POSTCREATE)),
    path('api/basestockunit/<int:pk>/',
         views.BaseStockUnitViewSet.as_view(GETRETRIEVE_PUTUPDATE_POSTDESTROY)),
    path('api/alternatestockunit',
         views.AlternateStockUnitViewSet.as_view(GETLIST_POSTCREATE)),
    path('api/alternatestockunit/<int:pk>/',
         views.AlternateStockUnitViewSet.as_view(GETRETRIEVE_PUTUPDATE_POSTDESTROY)),
]
