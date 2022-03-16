from django.urls import path
from core import views

urlpatterns = [
    # Costing Measures List View
    path('api/utils/costingmeasures', views.CostingMeasuresListView.as_view())
]