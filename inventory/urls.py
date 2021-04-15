from django.urls import path
from inventory import views

GETLIST_POSTCREATE = {'get': 'list', 'post': 'create'}
GETRETRIEVE_PUTUPDATE_POSTDESTROY = {'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}

urlpatterns = [
     # ITEM
     path('api/items',
          views.ItemViewSet.as_view(GETLIST_POSTCREATE)),
     path('api/items/<int:pk>/',
          views.ItemViewSet.as_view(GETRETRIEVE_PUTUPDATE_POSTDESTROY)),
     
     # ITEM STOCKS
     path('api/items/<int:pk>/stocks',
          views.ItemStockRetrieveViewSet.as_view({'get': 'retrieve'})),
     path('api/items/<int:pk>/stocks/list',
          views.ItemStockListViewSet.as_view({'get': 'list'})),
     path('api/items/<int:pk>/stocks/deposit',
          views.ItemDepositStockViewSet.as_view({'post': 'create'})),
     path('api/items/<int:pk>/stocks/request',
          views.ItemWithdrawStocksViewSet.as_view({'post': 'create'})),
     path('api/items/<int:pk>/stocks/history',
          views.StockMovementViewSet.as_view({'get': 'list'})),
     path('api/items/<int:pk>/itemrequestgroups/list',
          views.ItemRequestGroupItemDetailViewSet.as_view({'get': 'list'})),

     # ITEM PROPERTIES
     path('api/items/properties',
          views.ItemPropertiesListCreateViewSet.as_view(GETLIST_POSTCREATE)), 
     path('api/items/properties/<int:pk>/',
          views.ItemPropertiesViewSet.as_view(GETRETRIEVE_PUTUPDATE_POSTDESTROY)),

     # ITEM REQUEST GROUP / ITEM REQUESTS
     path('api/itemrequestgroups/list',
          views.ItemRequestGroupViewSet.as_view({'get': 'list'})),
     path('api/itemrequestgroups/<int:pk>/',
          views.ItemRequestGroupViewSet.as_view({'get': 'retrieve'})), 
     path('api/itemrequests/<int:pk>/',
          views.ItemRequestViewSet.as_view({'get': 'retrieve'})),
     path('api/itemrequests/<int:pk>/update',
          views.ItemRequestViewSet.as_view({'put': 'update'})),

     # STOCK REQUESTS
     path('api/stockrequests/<int:pk>/',
          views.StockRequestViewSet.as_view({'delete': 'destroy'})),

     # STOCK UNIT OF MEASURES
     path('api/basestockunit',
          views.BaseStockUnitViewSet.as_view(GETLIST_POSTCREATE)),
     path('api/basestockunit/<int:pk>/',
          views.BaseStockUnitViewSet.as_view(GETRETRIEVE_PUTUPDATE_POSTDESTROY)),
     path('api/alternatestockunit',
          views.AlternateStockUnitViewSet.as_view(GETLIST_POSTCREATE)),
     path('api/alternatestockunit/<int:pk>/',
          views.AlternateStockUnitViewSet.as_view(GETRETRIEVE_PUTUPDATE_POSTDESTROY)),
]
