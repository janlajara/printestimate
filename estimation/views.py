from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets, mixins
from rest_framework.response import Response
from estimation.models import Workstation, Activity, ActivityExpense, Speed, Operation, OperationStep
from estimation import serializers


# Create your views here.
class WorkstationViewSet(viewsets.ModelViewSet):
    queryset = Workstation.objects.all()
    serializer_class = serializers.WorkstationSerializer


class WorkstationActivitiesViewSet(mixins.ListModelMixin, 
                                    mixins.CreateModelMixin,
                                    viewsets.GenericViewSet):

    def get_serializer_class(self):
        if self.action == 'create':
            return serializers.ActivityCreateSerializer
        else:
            return serializers.ActivitySerializer

    def get_queryset(self):
        pk = self.kwargs.get('pk', None)
        if pk is not None:
            return Activity.objects.filter(workstation=pk)
        else:
            return Activity.objects.all()

    def create(self, request, pk=None):
        if pk is not None:
            workstation = get_object_or_404(Workstation, pk=pk)
            deserialized = serializers.ActivityCreateSerializer(data=request.data)

            if deserialized.is_valid():
                validated_data = deserialized.validated_data
                
                speed_data = validated_data.pop('speed', None)
                speed = Speed.objects.create(**speed_data)

                set_up = validated_data.pop('set_up')
                tear_down = validated_data.pop('tear_down')

                activity = workstation.add_activity(
                    speed=speed, set_up=set_up.hr, tear_down=tear_down.hr,
                    **validated_data)
                serialized = serializers.ActivitySerializer(activity)
                return Response(serialized.data)
            else:  
                return Response({'error': deserialized.errors})
        else:
            return Response({'error': "missing workstation pk"})


class WorkstationActivityExpensesViewSet(mixins.ListModelMixin, 
                                    mixins.CreateModelMixin,
                                    viewsets.GenericViewSet):
    serializer_class = serializers.ActivityExpenseSerializer

    def get_queryset(self):
        pk = self.kwargs.get('pk', None)
        if pk is not None:
            return ActivityExpense.objects.filter(workstation=pk)
        else:
            return ActivityExpense.objects.all()
    
    def create(self, request, pk=None):
        if pk is not None:
            workstation = get_object_or_404(Workstation, pk=pk)
            deserialized = serializers.ActivityExpenseSerializer(data=request.data)

            if deserialized.is_valid():
                validated_data = deserialized.validated_data
                expense = workstation.add_expense(**validated_data)
                serialized = serializers.ActivityExpenseSerializer(expense)
                return Response(serialized.data)
            else:
                return Response(deserialized.errors)
        else:
            return Response({'error': 'missing workstation pk'})


class WorkstationOperationsViewSet(mixins.ListModelMixin,
                            mixins.CreateModelMixin,
                            viewsets.GenericViewSet):
    serializer_class = serializers.OperationSerializer

    def get_queryset(self):
        pk = self.kwargs.get('pk', None)
        if pk is not None:
            return Operation.objects.filter(workstation=pk)
        else:
            return Operations.objects.all()

    def create(self, request, pk=None):
        if pk is not None:
            workstation = get_object_or_404(Workstation, pk=pk)
            deserialized = serializers.OperationSerializer(data=request.data)

            if deserialized.is_valid():
                validated_data = deserialized.validated_data
                operation = workstation.add_operation(**validated_data)
                serialized = serializers.OperationSerializer(operation)
                return Response(serialized.data)
            else:
                return Response(deserialized.errors)
        else:
            return Response({'error': 'missing workstation pk'})


class ActivityExpenseViewSet(mixins.RetrieveModelMixin, mixins.UpdateModelMixin,
                            mixins.DestroyModelMixin, viewsets.GenericViewSet):
    queryset = ActivityExpense.objects.all()
    serializer_class = serializers.ActivityExpenseSerializer


class ActivityViewSet(mixins.RetrieveModelMixin, mixins.UpdateModelMixin,
                    mixins.DestroyModelMixin, viewsets.GenericViewSet):
    queryset = Activity.objects.all()
    serializer_class = serializers.ActivitySerializer


class ActivityRelatedExpensesViewSet(mixins.ListModelMixin,
                            mixins.CreateModelMixin,
                            viewsets.GenericViewSet):
    serializer_class = serializers.ActivityExpenseSerializer

    def get_queryset(self):
        pk = self.kwargs.get('pk', None)
        if pk is not None:
            return ActivityExpense.objects.filter(activities__pk=pk)
        else:
            return ActivityExpense.objects.all()
    
    def create(self, request, pk=None):
        if pk is not None:
            activity = get_object_or_404(Activity, pk=pk)
            deserialized = serializers.ActivityExpenseSerializer(data=request.data)

            if deserialized.is_valid():
                validated_data = deserialized.validated_data
                expense = activity.add_expense(**validated_data)
                serialized = serializers.ActivityExpenseSerializer(expense)
                return Response(serialized.data)
            else:
                return Response(deserialized.errors)
        else:
            return Response({'error': 'missing activity pk'})


class OperationsViewSet(mixins.RetrieveModelMixin, mixins.UpdateModelMixin,
                        mixins.DestroyModelMixin, viewsets.GenericViewSet):
    queryset = Operation.objects.all()
    serializer_class = serializers.OperationSerializer


class OperationRelatedStepsViewSet(mixins.ListModelMixin,
                            mixins.CreateModelMixin,
                            viewsets.GenericViewSet):

    def get_serializer_class(self):
        if self.action == 'list':
            return serializers.OperationStepListSerializer
        else:
            return serializers.OperationStepSerializer

    def get_queryset(self):
        pk = self.kwargs.get('pk', None)
        if pk is not None:
            return OperationStep.objects.filter(operation__pk=pk).order_by('sequence')
        else:
            return OperationStep.objects.all()
    
    def create(self, request, pk=None):
        if pk is not None:
            operation = get_object_or_404(Operation, pk=pk)
            deserialized = serializers.OperationStepSerializer(data=request.data)

            if deserialized.is_valid():
                validated_data = deserialized.validated_data
                operation_step = operation.add_step(**validated_data)
                serialized = serializers.OperationStepSerializer(operation_step)
                return Response(serialized.data)
            else:
                return Response(deserialized.errors)
        else:
            return Response({'error': 'missing operation pk'})


class OperationStepViewSet(mixins.RetrieveModelMixin, mixins.UpdateModelMixin,
                        mixins.DestroyModelMixin, viewsets.GenericViewSet):
    queryset = OperationStep.objects.all()
    serializer_class = serializers.OperationStepSerializer
    
    def update(self, request, pk=None):
        operation_step = get_object_or_404(OperationStep, pk=pk)
        deserialized = serializers.OperationStepSerializer(data=request.data)

        if deserialized.is_valid():
            validated_data = deserialized.validated_data
            sequence = validated_data.pop('sequence')

            if sequence != operation_step.sequence:
                operation_step.move_step(sequence)

            OperationStep.objects.filter(pk=pk).update(**validated_data)
            operation_step = OperationStep.objects.get(pk=pk)
            serialized = serializers.OperationStepSerializer(operation_step)

            return Response(serialized.data)
        else:
            return Response(deserialized.errors)

    def destroy(self, request, pk=None):
        operation_step = get_object_or_404(OperationStep, pk=pk)
        serialized = serializers.OperationStepSerializer(operation_step)

        operation_step.delete_step()
        return Response(serialized.data)