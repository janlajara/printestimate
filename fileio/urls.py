from django.urls import path, include

urlpatterns = [
    path('', include('fileio.inventory.urls'))
]
