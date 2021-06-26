from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets, mixins
from rest_framework.response import Response
from estimation.models import Workstation, Activity, ActivityExpense, Speed
from estimation import serializers


# Create your views here.
class WorkstationViewSet(viewsets.ModelViewSet):
    queryset = Workstation.objects.all()
    serializer_class = serializers.WorkstationSerializer


class WorkstationActivitiesViewSet(mixins.ListModelMixin, 
                                    mixins.CreateModelMixin,
                                    viewsets.GenericViewSet):
    serializer_class = serializers.ActivitySerializer

    def get_queryset(self):
        pk = self.kwargs.get('pk', None)
        if pk is not None:
            return Activity.objects.filter(workstation=pk)
        else:
            return Activity.objects.all()

    def create(self, request, pk=None):
        if pk is not None:
            workstation = get_object_or_404(Workstation, pk=pk)
            deserialized = serializers.ActivitySerializer(data=request.data)
            
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


class ActivityExpenseViewSet(viewsets.ModelViewSet):
    queryset = ActivityExpense.objects.all()