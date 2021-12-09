from django.urls import path
from estimation import views

urlpatterns = [
    # Machine Viewsets
    path('api/machines', views.MachineViewSet.as_view({'get': 'list'})),
    path('api/machines/types', views.MachineTypesViewSet.as_view({'get': 'list'})),
    path('api/machines/sheetfedpress', 
        views.SheetFedPressMachineViewSet.as_view({'get': 'list', 'post': 'create'})),
    path('api/machines/sheetfedpress/<pk>/', 
        views.SheetFedPressMachineViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'})),
    path('api/machines/sheetfedpress/<pk>/parentsheets', 
        views.SheetFedPressMachineParentSheetViewSet.as_view({'get': 'list', 'post': 'create'})),
    path('api/machines/sheetfedpress/<pk>/childsheets', 
        views.SheetFedPressMachineChildSheetViewSet.as_view({'get': 'list', 'post': 'create'})),
    path('api/machines/sheetfedpress/<pk>/getlayout', 
        views.SheetFedPressMachineGetSheetLayoutsView.as_view({'post': 'create'})),

    # ParentSheet Viewsets
    path('api/parentsheets/<pk>/',
        views.ParentSheetViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'})),

    # ChildSheet Viewsets
    path('api/childsheets/getlayout',
        views.GetSheetLayoutsView.as_view({'post': 'create'})),
    path('api/childsheets/layout',
        views.ChildSheetLayoutView.as_view({'post': 'create'})),
    path('api/childsheets/<pk>/',
        views.ChildSheetViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'})),
]