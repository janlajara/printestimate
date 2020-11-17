from django.urls import path
from inventory import views


urlpatterns = [
    path('api/item', views.ItemViewSet.as_view({'get': 'list'})),
    path('api/item/<int:pk>/', views.ItemViewSet.as_view({'get': 'retrieve', 'post': 'create'})),
]
