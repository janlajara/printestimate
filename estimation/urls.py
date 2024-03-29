from django.urls import path, include

urlpatterns = [
    path('', include('estimation.costaddons.urls')),
    path('', include('estimation.process.urls')),
    path('', include('estimation.machine.urls')),
    path('', include('estimation.metaproduct.urls')),
    path('', include('estimation.template.urls')),
    path('', include('estimation.product.urls')) 
]
