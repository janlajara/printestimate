from django.urls import path
from inventory import views

GETLIST_POSTCREATE = {'get': 'list', 'post': 'create'}
GETRETRIEVE_PUTUPDATE_POSTDESTROY = {'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}

urlpatterns = [
     path('api/items',
          views.ItemViewSet.as_view(GETLIST_POSTCREATE)),
     path('api/items/<int:pk>/',
          views.ItemViewSet.as_view(GETRETRIEVE_PUTUPDATE_POSTDESTROY)),
     path('api/items/<int:pk>/stocks',
          views.ItemStockRetrieveViewSet.as_view({'get': 'retrieve'})),
     path('api/items/<int:pk>/stocks/list',
          views.ItemStockListViewSet.as_view({'get': 'list'})),
     path('api/items/<int:pk>/stocks/deposit',
          views.ItemDepositStockViewSet.as_view({'post': 'create'})),
     path('api/items/<int:pk>/stocks/withdraw',
          views.ItemWithdrawStocksViewSet.as_view({'post': 'create'})),
     path('api/items/<int:pk>/stocks/history',
          views.StockMovementSerializer.as_view({'get': 'list'})),
     path('api/items/<int:pk>/stockrequests/list',
          views.ItemStockRequestGroupListViewSet.as_view({'get': 'list'})),
     path('api/items/properties',
          views.ItemPropertiesListCreateViewSet.as_view(GETLIST_POSTCREATE)), 
     path('api/items/properties/<int:pk>/',
          views.ItemPropertiesViewSet.as_view(GETRETRIEVE_PUTUPDATE_POSTDESTROY)),
     path('api/stockrequests/list',
          views.StockRequestGroupListViewSet.as_view({'get': 'list'})),
     path('api/basestockunit',
          views.BaseStockUnitViewSet.as_view(GETLIST_POSTCREATE)),
     path('api/basestockunit/<int:pk>/',
          views.BaseStockUnitViewSet.as_view(GETRETRIEVE_PUTUPDATE_POSTDESTROY)),
     path('api/alternatestockunit',
          views.AlternateStockUnitViewSet.as_view(GETLIST_POSTCREATE)),
     path('api/alternatestockunit/<int:pk>/',
          views.AlternateStockUnitViewSet.as_view(GETRETRIEVE_PUTUPDATE_POSTDESTROY)),
]
