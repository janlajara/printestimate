from django.urls import path
from fileio.estimation import views

urlpatterns = [
    path('api/estimation/costestimates/<int:pk>/', views.CostEstimateView.as_view())
]