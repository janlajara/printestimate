from django.urls import path
from fileio.inventory import views

urlpatterns = [
    path('api/inventory/items', views.ItemsWorkbookView.as_view())
]