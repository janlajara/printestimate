from rest_framework import serializers
from rest_polymorphic.serializers import PolymorphicSerializer
from core.utils.measures import MeasurementSerializerField
from djmoney.contrib.django_rest_framework import MoneyField
from estimation.models import Workstation, ActivityExpense, \
    Activity, Speed, Operation, OperationStep


class WorkstationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Workstation
        fields = ['id', 'name']


class SpeedSerializer(serializers.ModelSerializer):
    rate = serializers.SerializerMethodField()

    class Meta:
        model = Speed
        fields = ['id', 'measure_value', 
            'measure_unit', 'speed_unit',
            'measure', 'rate']

    def get_rate(self, obj):
        return str(obj.rate)


class ActivityExpenseSerializer(serializers.ModelSerializer):
    rate = MoneyField(max_digits=14, decimal_places=2)

    class Meta:
        model = ActivityExpense
        fields = ['id', 'name', 'type', 'rate'] 


class ActivitySerializer(serializers.ModelSerializer):
    speed = SpeedSerializer()
    set_up = MeasurementSerializerField()
    tear_down = MeasurementSerializerField()
    activity_expenses = ActivityExpenseSerializer(many=True, read_only=True)

    class Meta:
        model = Activity
        fields = ['id', 'name', 'speed', 'set_up', 'tear_down', 'activity_expenses',
            'measure', 'measure_unit', 'flat_rate', 'measure_rate']


class OperationStepSerializer(serializers.ModelSerializer):
    class Meta:
        model = OperationStep
        fields = ['id', 'activity', 'sequence', 'notes']


class OperationSerializer(serializers.ModelSerializer):
    operation_steps = OperationStepSerializer(many=True)

    class Meta:
        model = Operation
        fields = ['id', 'name', 'costing_measure', 
            'material_type', 'operation_steps']