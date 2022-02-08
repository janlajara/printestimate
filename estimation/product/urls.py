from django.urls import path
from estimation.product import views

urlpatterns = [
    # Product Template Viewsets
    path('api/products/estimates', 
        views.ProductEstimateView.as_view({'post':'create'})),
]