from django.db import migrations
from core.utils.measures import CostingMeasure
from estimation.metaproduct.models import MetaProduct, MetaComponent, \
    MetaEstimateVariable, MetaOperation
from estimation.process.models import Operation
from estimation.machine.models import Machine
from inventory.models import Item

def create_product_class(apps, schema_editor):
    def _create_meta_product(**kwargs):
        return MetaProduct.objects.create(**kwargs)

    def _create_components(product, components_data):
        for component_data in components_data:
            materials = component_data.pop('materials')
            machine_name = component_data.pop('machine') if 'machine' in component_data else None
            component = product.add_meta_component(**component_data)

            if machine_name is not None:
                machine = Machine.objects.filter(name=machine_name).first()
                if machine is not None:
                    component.add_meta_machine_option(machine)

            for material_name in materials:
                material = Item.objects.filter(name=material_name).first()

                if material is not None:
                    component.add_meta_material_option(material)

    def _create_services(product, services_data):
        for service_data in services_data:
            component_name = service_data.pop('component') if 'component' in service_data else None
            operations_data = service_data.pop('operations')
            if component_name is not None:
                component = product.meta_product_datas.get(name=component_name)
                service = product.add_meta_service(meta_component=component, **service_data)
            else:
                service = product.add_meta_service(**service_data)

            for operation_data in operations_data:
                options_data = operation_data.pop('options')
                meta_operation = service.add_meta_operation(**operation_data)

                for option_name in options_data:
                    operation_option = Operation.objects.filter(name=option_name).first()
                    meta_operation.add_option(operation_option)


    dataset = [
        {'name': 'Carbonless Form', 'description': 'Class for all carbonless forms.',
            'components': [
                {'name': 'Form', 'type': Item.PAPER, 'allow_multiple_materials': True,
                    'machine': 'Heidelberg GTO',
                    'materials': ['Carbonless White', 'Carbonless Yellow', 'Carbonless Blue']},
                {'name': 'Backing', 'type': Item.PAPER, 'allow_multiple_materials': False,
                    'materials': ['Kraft #80']}
            ],
            'services': [
                {'name': 'Layout', 'type': Item.OTHER, 'uom': 'layout',
                    'costing_measure': CostingMeasure.QUANTITY, 
                    'operations': [
                        {'name': 'Create Layout', 'options_type': MetaOperation.SINGLE_OPTION,
                            'options': ['Creatives Layout Operation']}
                    ]},
                {'name': 'Form Raw-to-Running Cut', 'type': Item.PAPER,  'uom': 'count',
                    'costing_measure': CostingMeasure.QUANTITY, 
                    'component': 'Form', 'estimate_variable_type': MetaEstimateVariable.RAW_TO_RUNNING_CUT,
                    'operations': [
                        {'name': 'Cut Sheet', 'options_type': MetaOperation.SINGLE_OPTION,
                            'options': ['Polar Cutting Operation']}
                    ]},
                {'name': 'Backing Raw-to-Running Cut', 'type': Item.PAPER,  'uom': 'count',
                    'costing_measure': CostingMeasure.QUANTITY, 
                    'component': 'Backing', 'estimate_variable_type': MetaEstimateVariable.RAW_TO_FINAL_CUT,
                    'operations': [
                        {'name': 'Cut Sheet', 'options_type': MetaOperation.SINGLE_OPTION,
                            'options': ['Polar Cutting Operation']}
                    ]},
                {'name': 'Printing', 'type': Item.PAPER,  'uom': 'sheet',
                    'costing_measure': CostingMeasure.QUANTITY, 
                    'component': 'Form', 'estimate_variable_type': MetaEstimateVariable.MACHINE_RUN,
                    'operations': [
                        {'name': 'Front Print', 'options_type': MetaOperation.SINGLE_OPTION,
                            'options': ['GTO 2-Color Printing', 'KORSE 2-Color Printing']}
                    ]},
                {'name': 'Form Running-to-Final Cut', 'type': Item.PAPER,  'uom': 'count',
                    'costing_measure': CostingMeasure.QUANTITY, 
                    'component': 'Form', 'estimate_variable_type': MetaEstimateVariable.RUNNING_TO_FINAL_CUT,
                    'operations': [
                        {'name': 'Cut Sheet', 'options_type': MetaOperation.SINGLE_OPTION,
                            'options': ['Polar Cutting Operation']}
                    ]},
                {'name': 'Gathering', 'type': Item.PAPER,  'uom': 'set',
                    'costing_measure': CostingMeasure.QUANTITY, 
                    'component': 'Form', 'estimate_variable_type': MetaEstimateVariable.TOTAL_MATERIAL,
                    'operations': [
                        {'name': 'Collate Sheets', 'options_type': MetaOperation.SINGLE_OPTION,
                            'options': ['Finishing Gathering Operation']}
                    ]},
                {'name': 'Padding', 'type': Item.PAPER,  'uom': 'pad',
                    'costing_measure': CostingMeasure.QUANTITY, 
                    'component': 'Form', 'estimate_variable_type': MetaEstimateVariable.SET_MATERIAL,
                    'operations': [
                        {'name': 'Pad Sheets', 'options_type': MetaOperation.SINGLE_OPTION,
                            'options': ['Finishing Padding Operation']}
                    ]},
            ]
        }
    ]

    for data in dataset:
        components_data = data.pop('components')
        services_data = data.pop('services')
        product = _create_meta_product(**data)

        _create_components(product, components_data)
        _create_services(product, services_data)


class Migration(migrations.Migration):

    dependencies = [
        ('estimation', '0001_initial'),
        ('estimation', '1001_generate_test_data_workstations'),
        ('inventory', '1001_generate_test_data')
    ]

    operations = [
        migrations.RunPython(create_product_class, reverse_code=migrations.RunPython.noop),
    ]
