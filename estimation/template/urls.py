from django.urls import path
from estimation.template import views

urlpatterns = [
    # Product Template Viewsets
    path('api/templates/products', 
        views.ProductTemplateViewSet.as_view({'get': 'list', 'post':'create'})),
    path('api/templates/products/<pk>/', 
        views.ProductTemplateViewSet.as_view({'get': 'retrieve', 'put': 'update', 
            'delete': 'destroy'})),
]