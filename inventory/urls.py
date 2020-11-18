from django.urls import path
from inventory import views

GETLIST_POSTCREATE = {'get': 'list', 'post': 'create'}
GETRETRIEVE_PUTUPDATE = {'get': 'retrieve', 'put': 'update'}

urlpatterns = [
    path('api/item',
         views.ItemViewSet.as_view(GETLIST_POSTCREATE)),
    path('api/item/<int:pk>/',
         views.ItemViewSet.as_view(GETRETRIEVE_PUTUPDATE)),
    path('api/basestockunit',
         views.BaseStockUnitViewSet.as_view(GETLIST_POSTCREATE)),
    path('api/basestockunit/<int:pk>/',
         views.BaseStockUnitViewSet.as_view(GETRETRIEVE_PUTUPDATE)),
    path('api/alternatestockunit',
         views.AlternateStockUnitViewSet.as_view(GETLIST_POSTCREATE)),
    path('api/alternatestockunit/<int:pk>/',
         views.AlternateStockUnitViewSet.as_view(GETRETRIEVE_PUTUPDATE)),
]
