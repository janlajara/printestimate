from django.urls import path, include

urlpatterns = [
    path('', include('estimation.process.urls')),
    path('', include('estimation.machine.urls'))
]
