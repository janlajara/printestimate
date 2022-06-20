from django.db import migrations
from estimation.costaddons.models import ConfigCostAddon, TemplateCostAddonSet


def create_costaddons(apps, schema_editor):
    def _create(**kwargs):
        return ConfigCostAddon.objects.create(**kwargs)
    
    dataset = [
        {'name': 'Delivery Fee', 'type': ConfigCostAddon.FLAT,
            'allow_custom_value': True,
            'options': [
                {'value': 1000, 'label': 'Manila'},
                {'value': 500, 'label': 'Sta. Rosa'},
                {'value': 300, 'label': 'Calamba'}
            ]},
        {'name': 'Mark-up', 'type': ConfigCostAddon.PERCENTAGE,
            'allow_custom_value': True,
            'options': [
                {'value': 20, 'label': 'Low'},
                {'value': 30, 'label': 'Mid'},
                {'value': 40, 'label': 'High'}
            ]},
        {'name': 'Sales Tax', 'type': ConfigCostAddon.PERCENTAGE,
            'allow_custom_value': False,
            'options': [
                {'value': 12, 'label': 'VAT'},
                {'value': 0, 'label': 'Non-VAT'},
                {'value': 0, 'label': 'Zero-rated'}
            ]}
    ]

    for data in dataset:
        options = data.pop('options')
        cost_addon = _create(**data)
        
        for option in options:
            cost_addon.add_option(**option)



def create_templates(apps, schema_editor):
    def _create(**kwargs):
        return TemplateCostAddonSet.objects.create(**kwargs)

    dataset = [
        {'name': 'Standard', 'is_default': True,
            'items': ['Delivery Fee', 'Mark-up', 'Sales Tax']},
        {'name': 'Pick-up only', 'is_default': False,
            'items': ['Mark-up', 'Sales Tax']}
    ]

    for data in dataset:
        items = data.pop('items')
        template = _create(**data)

        for item_name in items:
            result = ConfigCostAddon.objects.filter(name=item_name)
            if result is not None:
                item = result.first()
                template.add_item(item)


class Migration(migrations.Migration):

    dependencies = [
        ('estimation', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_costaddons, reverse_code=migrations.RunPython.noop),
        migrations.RunPython(create_templates, reverse_code=migrations.RunPython.noop)
    ]
