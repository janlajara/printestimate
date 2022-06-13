from django.urls import path
from fileio.inventory import views

urlpatterns = [
    path('api/items', views.ItemsWorkbookView.as_view())
]