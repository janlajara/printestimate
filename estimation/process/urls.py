from django.urls import path
from estimation import views

urlpatterns = [
    # Workstation Viewsets
    path('api/workstations', 
        views.WorkstationViewSet.as_view({'get': 'list', 'post':'create'})),
    path('api/workstations/<int:pk>/',
        views.WorkstationViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'})),
    path('api/workstations/<int:pk>/activities',
        views.WorkstationActivitiesViewSet.as_view({'get': 'list', 'post': 'create'})),
    path('api/workstations/<int:pk>/activityexpenses',
        views.WorkstationActivityExpensesViewSet.as_view({'get': 'list', 'post': 'create'})),
    path('api/workstations/<int:pk>/operations',
        views.WorkstationOperationsViewSet.as_view({'get': 'list', 'post': 'create'})),

    # Activity Expense Viewsets
    path('api/activityexpenses/<int:pk>/',
        views.ActivityExpenseViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'})),

    # Activity Viewsets
    path('api/activities/<int:pk>/',
        views.ActivityViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'})),
    path('api/activities/<int:pk>/activityexpenses',
        views.ActivityRelatedExpensesViewSet.as_view({'get': 'list', 'post': 'create'})),
    
    # Operation Viewsets
    path('api/operations',
        views.OperationsViewSet.as_view({'get': 'list'})),
    path('api/operations/costingmeasures',
        views.CostingMeasureView.as_view({'get': 'list'})),
    path('api/operations/<int:pk>/',
        views.OperationsViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'})),
    path('api/operations/<int:pk>/steps',
        views.OperationRelatedStepsViewSet.as_view({'get': 'list', 'post': 'create'})),

    # Operation Step Viewsets
    path('api/operationsteps/<int:pk>/',
        views.OperationStepViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'})),

]