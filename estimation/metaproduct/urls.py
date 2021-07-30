from django.urls import path
from estimation import views

urlpatterns = [
    # MetaProduct Viewsets
    path('api/metaproducts', 
        views.MetaProductViewSet.as_view({'get': 'list', 'post':'create'})),
    path('api/metaproducts/<pk>/', 
        views.MetaProductViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'})),
    path('api/metaproducts/<pk>/metacomponents',
        views.MetaProductComponentViewSet.as_view({'get': 'list', 'post': 'create'})),

    # MetaComponent Viewsets
    path('api/metacomponents/<pk>/',
        views.MetaComponentViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'})),
]