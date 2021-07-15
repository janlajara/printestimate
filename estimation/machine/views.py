from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets, mixins
from rest_framework.response import Response
from estimation.models import Machine, SheetFedPressMachine, ParentSheet, ChildSheet
from estimation import serializers


class MachineTypesViewSet(viewsets.ViewSet):
    def list(self, request):
        types = map(
            lambda x: { "value": x[0], "display": x[1]},
            Machine.TYPES)
        return Response(types)


class SheetFedPressMachineViewSet(mixins.ListModelMixin, mixins.CreateModelMixin, 
                            viewsets.GenericViewSet):
    queryset = SheetFedPressMachine.objects.all()
    serializer_class = serializers.SheetFedPressMachineSerializer

    def create(self, request):
        deserialized = serializers.SheetFedPressMachineSerializer(data=request.data)

        if deserialized.is_valid():
            validated_data = deserialized.validated_data
            machine = Machine.objects.create_machine(**validated_data)
            serialized = serializers.SheetFedPressMachineSerializer(machine)
            
            return Response(serialized.data)
        else:
            return Response(deserialized.errors)