from django.urls import path
from core import views

urlpatterns = [
    path('api/measures/units', 
        views.MeasureUnitsView.as_view({'get': 'list'}))
]