from rest_framework import serializers
from rest_polymorphic.serializers import PolymorphicSerializer
from measurement.measures import Time
from core.utils.measures import MeasurementSerializerField
from djmoney.contrib.django_rest_framework import MoneyField
from estimation.models import Workstation, ActivityExpense, \
    Activity, Speed, Operation, OperationStep


class WorkstationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Workstation
        fields = ['id', 'name', 'description']


class SpeedSerializer(serializers.ModelSerializer):
    rate = serializers.SerializerMethodField()

    class Meta:
        model = Speed
        fields = ['id', 'measure_value', 
            'measure_unit', 'speed_unit',
            'measure', 'rate']

    def get_rate(self, obj):
        return obj.rate_formatted


class ActivityExpenseSerializer(serializers.ModelSerializer):
    rate = MoneyField(max_digits=14, decimal_places=2)
    rate_formatted = serializers.SerializerMethodField()

    class Meta:
        model = ActivityExpense
        fields = ['id', 'name', 'type', 'rate', 'rate_formatted']

    def get_rate_formatted(self, obj):
        formatted = '%s / %s' % (obj.rate, obj.type)
        if obj.type == ActivityExpense.FLAT:
            formatted = '%s %s' % (obj.rate, obj.type)
        return formatted


class ActivitySerializer(serializers.ModelSerializer):
    speed = SpeedSerializer()
    set_up = MeasurementSerializerField(display_unit='hr')
    tear_down = MeasurementSerializerField(display_unit='hr')
    flat_rate = MoneyField(max_digits=14, decimal_places=2, read_only=True)
    measure_rate = MoneyField(max_digits=14, decimal_places=2, read_only=True)
    hourly_rate = MoneyField(max_digits=14, decimal_places=2, read_only=True)
    flat_rate_formatted = serializers.SerializerMethodField()
    measure_rate_formatted = serializers.SerializerMethodField()
    hourly_rate_formatted = serializers.SerializerMethodField()

    class Meta:
        model = Activity
        fields = ['id', 'name', 'speed', 'set_up', 'tear_down', 
            'activity_expenses', 'measure', 'measure_unit', 
            'flat_rate', 'flat_rate_formatted', 
            'measure_rate', 'measure_rate_formatted', 
            'hourly_rate', 'hourly_rate_formatted']

    def get_flat_rate_formatted(self, obj):
        return str(obj.flat_rate)
    
    def get_measure_rate_formatted(self, obj):
        return '%s / %s' % (str(obj.measure_rate), obj.measure_unit)
    
    def get_hourly_rate_formatted(self, obj):
        return '%s / hr' % str(obj.hourly_rate)

    def create(self, validated_data):
        speed_data = validated_data.pop('speed')
        speed = Speed.objects.create(**speed_data)
        return Activity.objects.create(speed=speed, **validated_data)

    def update(self, instance, validated_data):
        speed = validated_data.pop('speed')
        if speed is not None:
            Speed.objects.filter(pk=instance.speed.id).update(**speed)
        super().update(instance, validated_data)
        return Activity.objects.get(pk=instance.id)


class ActivityCreateSerializer(serializers.ModelSerializer):
    speed = SpeedSerializer()
    set_up = MeasurementSerializerField(required=False, default=Time(hr=0))
    tear_down = MeasurementSerializerField(required=False, default=Time(hr=0))
    include_presets = serializers.BooleanField(default=False)

    class Meta:
        model = Activity
        fields = ['id', 'name', 'speed', 'set_up', 'tear_down', 
            'measure', 'measure_unit', 'flat_rate', 'measure_rate', 
            'include_presets', 'activity_expenses']


class OperationStepSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False, allow_null=True)
    sequence = serializers.IntegerField(required=False)
    notes = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = OperationStep
        fields = ['sequence', 'id', 'activity', 'notes']


class OperationStepListSerializer(OperationStepSerializer):
    activity = ActivitySerializer(read_only=True)


class OperationSerializer(serializers.ModelSerializer):
    prerequisite = serializers.PrimaryKeyRelatedField(
        required=False, queryset=Operation.objects.all())
    operation_steps = OperationStepSerializer(many=True)

    class Meta:
        model = Operation
        fields = ['id', 'name', 'machine', 'material_type', 
            'costing_measure', 'prerequisite', 'operation_steps']


class OperationListSerializer(serializers.ModelSerializer):
    prerequisite = serializers.PrimaryKeyRelatedField(
        required=False, queryset=Operation.objects.all())
    operation_steps = serializers.SerializerMethodField() 

    class Meta:
        model = Operation
        fields = ['id', 'name', 'material_type', 'prerequisite', 
            'costing_measure', 'operation_steps']

    def get_operation_steps(self, instance):
        steps = instance.operation_steps.all().order_by('sequence')
        return OperationStepListSerializer(steps, many=True).data