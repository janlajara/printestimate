from django.db import migrations
from estimation.metaproduct.models import MetaProduct, MetaComponent, MetaService
from estimation.template.models import ProductTemplate

def create_product_template(apps, schema_editor):
    carbonless_class = MetaProduct.objects.get(name='Carbonless Form')
    callingcard_class = MetaProduct.objects.get(name='Calling Card')

    dataset = [
        {'name': 'Carbonless Form 8x11 100s 2ply', 
         'description': 'Carbonless Form 8x11; 100s; 2ply (W/Y); GTO Process;',
         'meta_product': carbonless_class,
         'components': [
            {'meta_component': 'Form', 'quantity': 100, 
             'length_value':11, 'width_value':8, 'size_uom':'inch',
             'machine_option': 'Heidelberg GTO',
             'meta_material_options': ['Carbonless White', 'Carbonless Yellow']
            },
            {'meta_component': 'Backing', 'quantity': 1, 
             'length_value':11, 'width_value':8, 'size_uom':'inch',
             'meta_material_options': ['Kraft #80']
            }
         ],
         'services': [
            {'meta_service': 'Layout', 'input_quantity': 1,
             'operations': [
                {'name': 'Create Layout', 'options': ['Creatives Layout Operation']}
            ]},
            {'meta_service': 'Form Raw-to-Running Cut',
             'operations': [
                {'name': 'Cut Sheet', 'options': ['Polar Cutting Operation']}
            ]},
            {'meta_service': 'Backing Raw-to-Running Cut',
             'operations': [
                {'name': 'Cut Sheet', 'options': ['Polar Cutting Operation']}
            ]},
            {'meta_service': 'Printing',
             'operations': [
                {'name': 'Front Print', 'options': ['GTO 2-Color Printing']}
            ]},
            {'meta_service': 'Form Running-to-Final Cut',
             'operations': [
                {'name': 'Cut Sheet', 'options': ['Polar Cutting Operation']}
            ]},
            {'meta_service': 'Gathering',
             'operations': [
                {'name': 'Collate Sheets', 'options': ['Finishing Gathering Operation']}
            ]},
            {'meta_service': 'Padding',
             'operations': [
                {'name': 'Pad Sheets', 'options': ['Finishing Padding Operation']}
            ]}
         ]}
    ]

    for template_data in dataset:
        components_data = template_data.pop('components')
        services_data = template_data.pop('services')
        product_template = ProductTemplate.objects.create(**template_data)
        product_class = product_template.meta_product

        for component_data in components_data:
            meta_component_name = component_data.pop('meta_component')
            machine_option_name = component_data.pop('machine_option') if 'machine_option' in component_data else None
            material_options = component_data.pop('meta_material_options')
            component_class = product_class.meta_product_datas.get(name=meta_component_name)
            component_class = MetaComponent.objects.get(pk=component_class.pk)
            if machine_option_name is not None:
                machine_option_class = component_class.meta_machine_options.get(machine__name=machine_option_name)
                component_data['machine_option'] = machine_option_class

            component_template = product_template.add_component_template(
                meta_component=component_class, **component_data)

            for material_option in component_class.meta_material_options.filter(item__name__in=material_options).all():
                component_template.add_material_template(material_option)

        for service_data in services_data:
            meta_service_name = service_data.pop('meta_service')
            operations_data = service_data.pop('operations')
            meta_service = product_class.meta_product_datas.get(name=meta_service_name)
            meta_service = MetaService.objects.get(pk=meta_service.pk)
            service_template = product_template.add_service_template(
                meta_service=meta_service, **service_data)
            
            for operation_data in operations_data:
                operation_name = operation_data.pop('name')
                options_data = operation_data.pop('options')
                meta_operation = meta_service.meta_operations.get(name=operation_name)
                operation_template = service_template.add_operation_template(meta_operation=meta_operation)

                for option in meta_operation.meta_operation_options.filter(operation__name__in=options_data):
                    operation_template.add_operation_option_template(meta_operation_option=option)
                



class Migration(migrations.Migration):

    dependencies = [
        ('estimation', '1002_generate_test_data_productclasses')
    ]

    operations = [
        migrations.RunPython(create_product_template, reverse_code=migrations.RunPython.noop),
    ]
