from rest_framework import serializers
from django.shortcuts import get_object_or_404
from estimation.costaddons.models import ConfigCostAddon, ConfigCostAddonOption, \
    TemplateCostAddonSet, TemplateCostAddonItem


class ConfigCostAddonOptionSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False, allow_null=True)

    class Meta:
        model = ConfigCostAddonOption
        fields = ['id', 'label', 'value', 'formatted_value']


class ConfigCostAddonSerializer(serializers.ModelSerializer):
    config_cost_addon_options = ConfigCostAddonOptionSerializer(many=True)

    class Meta:
        model = ConfigCostAddon
        fields = ['id', 'name', 'type', 'allow_custom_value', 
            'symbol', 'config_cost_addon_options']

    def create(self, validated_data):
        options_data = validated_data.pop('config_cost_addon_options')
        instance = ConfigCostAddon.objects.create(**validated_data)

        for option in options_data:
            value = option.get('value')
            label = option.get('label')
            instance.add_option(value, label)

        return instance

    def update(self, instance, validated_data):
        def _delete_items(as_is_items, to_be_items):
            as_is_pks = [x.id for x in as_is_items]
            to_be_pks = [x.get('id') for x in to_be_items if 'id' in x]
            to_delete = [x for x in as_is_pks if x not in to_be_pks]
            ConfigCostAddonOption.objects.filter(pk__in=to_delete).delete()

        def _update_items(to_be_items):
            for item_data in to_be_items:
                existing_id = item_data.get('id')
                if existing_id is not None:
                    item_obj = get_object_or_404(ConfigCostAddonOption, pk=existing_id)
                    item_obj.value = item_data.get('value', item_obj.value)
                    item_obj.label = item_data.get('label', item_obj.label)
                    item_obj.save()
                else:
                    value = item_data.get('value')
                    label = item_data.get('label')
                    instance.add_option(value, label)
        
        instance.name = validated_data.get('name', instance.name)
        instance.type = validated_data.get('type', instance.type)
        instance.allow_custom_value = validated_data.get('allow_custom_value', instance.allow_custom_value)
        
        addon_options_data = validated_data.get('config_cost_addon_options', [])
        _delete_items(instance.config_cost_addon_options.all(), addon_options_data)
        _update_items(addon_options_data)

        instance.save()
        instance.refresh_from_db()
        return instance


class TemplateCostAddonItemSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    sequence = serializers.IntegerField(required=False)

    class Meta:
        model = TemplateCostAddonItem
        fields = ['id', 'sequence', 'config_cost_addon']

    def to_representation(self, instance):
        config_addon_serializer = ConfigCostAddonSerializer(
            instance.config_cost_addon)
        data = super().to_representation(instance)
        data['config_cost_addon'] = config_addon_serializer.data

        return data
        

class TemplateCostAddonSetSerializer(serializers.ModelSerializer):
    template_cost_addon_items = TemplateCostAddonItemSerializer(many=True)

    class Meta:
        model = TemplateCostAddonSet
        fields = ['id', 'name', 'is_default', 'template_cost_addon_items']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        addon_item_sorted = instance.template_cost_addon_items.all().order_by('sequence')
        addon_item_serializer = TemplateCostAddonItemSerializer(addon_item_sorted, many=True)
        data['template_cost_addon_items'] = addon_item_serializer.data
        return data

    def create(self, validated_data):
        items_data = validated_data.pop('template_cost_addon_items')
        instance = TemplateCostAddonSet.objects.create(**validated_data)

        for item_data in items_data:
            config_cost_addon = item_data.get('config_cost_addon')
            instance.add_item(config_cost_addon)

        return instance

    def update(self, instance, validated_data):
        def _delete_items(as_is_items, to_be_items):
            as_is_pks = [x.id for x in as_is_items]
            to_be_pks = [x.get('id') for x in to_be_items if 'id' in x]
            to_delete = [x for x in as_is_pks if x not in to_be_pks]
            TemplateCostAddonItem.objects.filter(pk__in=to_delete).delete()

        def _update_items(to_be_items):
            for (i, item_data) in enumerate(to_be_items):
                next_sequence = i+1
                config_cost_addon = item_data.get('config_cost_addon')
                existing_id = item_data.get('id')

                if existing_id is not None:
                    item_obj = get_object_or_404(TemplateCostAddonItem, pk=existing_id)
                    item_obj.sequence = next_sequence
                    item_obj.save()
                else:
                    instance.add_item(config_cost_addon, next_sequence)

        instance.name = validated_data.get('name', instance.name)
        is_default_data = validated_data.get('is_default')
        if is_default_data:
            instance.set_default()

        template_cost_addon_items_data = validated_data.get('template_cost_addon_items', [])
        _delete_items(instance.template_cost_addon_items.all(), template_cost_addon_items_data)
        _update_items(template_cost_addon_items_data)

        instance.save()
        instance.refresh_from_db()
        return instance

        
