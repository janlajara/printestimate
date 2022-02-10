from django.urls import path
from estimation.product import views

urlpatterns = [
    # Product Estimate View Set
    path('api/products/estimates', 
        views.ProductEstimateView.as_view({'get':'list', 'post':'create'})),
    path('api/products/estimates/<pk>/',
        views.ProductEstimateView.as_view({'get':'retrieve'}))
]