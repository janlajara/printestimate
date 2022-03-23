import pytest, math, time, multiprocessing
from core.utils.measures import CostingMeasure
from inventory.models import Item
from inventory.tests import item_factory, base_unit__sheet, alt_unit__ream
from estimation.template.tests import meta_product, gto_workstation, \
    gto_machine, finishing_workstation
from estimation.template.models import ProductTemplate
from estimation.product.models import ProductEstimate, Product, \
    Component, Material, EstimateQuantity, Service, OperationEstimate
from estimation.product import serializers
from estimation.machine.models import Machine


@pytest.fixture
def carbonless_item(db, item_factory):
    item = item_factory(type=Item.PAPER, name='Carbonless')
    item.properties.length_value = 28
    item.properties.width_value = 34
    item.properties.size_uom = 'inch'
    return item


@pytest.fixture
def gto_machine(db):
    return Machine.objects.create_machine(name='GTO Press', 
        type=Machine.SHEET_FED_PRESS, uom='inch',
        min_sheet_width=11, max_sheet_width=25,
        min_sheet_length=11, max_sheet_length=25)


@pytest.fixture
def product_template(db, item_factory, meta_product):
    product_template = ProductTemplate.objects.create(meta_product=meta_product,
        name=meta_product.name, description=meta_product.description)
    meta_component = meta_product.meta_product_datas.filter(name='Sheets').first()
    gto_machine_option = meta_component.meta_machine_options.filter(machine__name='GTO Press').first()
    component_template = product_template.add_component_template(
        meta_component, 100, machine_option=gto_machine_option, 
        length_value=11, width_value=8.5, size_uom='inch')

    for meta_material_option in meta_component.meta_material_options.all():
        component_template.add_material_template(meta_material_option)

    print_service = meta_product.meta_product_datas.filter(name='Printing').first()
    print_service_template = product_template.add_service_template(meta_service=print_service)
    print_meta_operation = print_service.meta_operations.filter(name='Front Print').first()
    print_operation_template = print_service_template.add_operation_template(print_meta_operation)
    print_meta_operation_option = print_meta_operation.meta_operation_options.filter(
        operation__name='GTO 2-color Printing').first()
    print_operation_template.add_operation_option_template(print_meta_operation_option)

    gathering_service = meta_product.meta_product_datas.filter(name='Gathering').first()
    gathering_service_template = product_template.add_service_template(meta_service=gathering_service)
    gathering_meta_operation = gathering_service.meta_operations.filter(name='Gathering').first()
    gathering_operation_template = gathering_service_template.add_operation_template(gathering_meta_operation)
    gathering_meta_operation_option = gathering_meta_operation.meta_operation_options.filter(
        operation__name='Gathering Operation').first()
    gathering_operation_template.add_operation_option_template(gathering_meta_operation_option)

    return product_template


def test_product_estimate__set_estimate_quantities(db, product_template):
    product_estimate = ProductEstimate.objects.create_product_estimate(
        product_template)
    product_estimate.set_estimate_quantities([100, 200, 300])

    order_quantities = product_estimate.order_quantities
    assert order_quantities is not None
    assert isinstance(order_quantities, list)
    assert order_quantities == [100, 200, 300]
    
    estimate_quantities = EstimateQuantity.objects.filter(product_estimate=product_estimate).all()
    assert estimate_quantities is not None
    assert len(estimate_quantities) == 3


def test_product_estimate__create_product_by_template(db, product_template):
    product_estimate = ProductEstimate.objects.create_product_estimate(
        product_template, [100, 200, 300])
    product = product_estimate.product

    assert product is not None
    product_components = product.components.all()
    assert product_components is not None and \
        len(product_components) == 1
    
    sheet_component = product_components.first()
    assert sheet_component.name == 'Sheets'
    assert sheet_component.machine is not None and sheet_component.machine.name == 'GTO Press'
    assert sheet_component.materials is not None and \
        len(sheet_component.materials.all()) == 3
    
    for material in sheet_component.materials.all():
        assert material.label in ['Carbonless White 8.5x11inch', 
            'Carbonless Blue 8.5x11inch', 'Carbonless Yellow 8.5x11inch']
        assert material.quantity == 100

    product_services = product.services.all()
    assert product_services is not None and \
        len(product_services) == 2

    printing_service = product.services.filter(name='Printing').first()
    assert printing_service is not None 
    assert printing_service.component == sheet_component
    assert printing_service.sequence == 1
    assert printing_service.costing_measure == 'quantity'
    assert printing_service.estimate_variable_type == 'Running Material'

    operation_estimates = printing_service.operation_estimates.all()
    assert operation_estimates is not None
    assert len(operation_estimates) == 3

    for operation_estimate in operation_estimates:
        assert operation_estimate.name == 'Front Print'
        assert operation_estimate.material.label in ['Carbonless White 8.5x11inch', 
            'Carbonless Blue 8.5x11inch', 'Carbonless Yellow 8.5x11inch']
        activity_estimates = operation_estimate.activity_estimates.all()
        assert activity_estimates is not None
        assert len(activity_estimates) == 2

        for (index, activity_estimate) in enumerate(activity_estimates):
            activity_estimate.name == 'Spot Color Printing'
            activity_estimate.sequence == index
            activity_estimate.notes in ['1st color', '2nd color']

            activity_expense_estimates = activity_estimate.activity_expense_estimates.all()
            assert activity_expense_estimates is not None
            assert len(activity_expense_estimates) == 3

            for activity_expense_estimate in activity_expense_estimates:
                assert activity_expense_estimate.name in ['Electricity', 'Depreciation', 'Ink']
                if activity_expense_estimate.name == 'Electricity':
                    assert activity_expense_estimate.rate.amount == 100
                    assert activity_expense_estimate.type == 'hour'
                elif activity_expense_estimate.name == 'Depreciation':
                    assert activity_expense_estimate.rate.amount == 200
                    assert activity_expense_estimate.type == 'hour'
                else:
                    assert activity_expense_estimate.rate.amount == 0.75
                    assert activity_expense_estimate.type == 'measure'



def test_product__estimate(db, product_template):
    product_estimate = ProductEstimate.objects.create_product_estimate(
        product_template, [100, 200, 300])

    assert product_estimate.estimates is not None
    assert product_estimate.order_quantities == [100, 200, 300]

    material_estimates = product_estimate.estimates.material_estimates
    material_estimate = material_estimates[0]
    assert len(material_estimate.estimates) == 3

    estimate_100 = material_estimate.estimates[0]
    assert estimate_100.order_quantity == 100
    assert estimate_100.material_quantity == 100
    assert estimate_100.estimated_stock_quantity == 2500
    assert estimate_100.spoilage_rate == 0
    assert estimate_100.estimated_spoilage_quantity == 0

    estimate_200 = material_estimate.estimates[1]
    assert estimate_200.order_quantity == 200
    assert estimate_200.material_quantity == 100
    assert estimate_200.estimated_stock_quantity == 5000
    assert estimate_200.spoilage_rate == 0
    assert estimate_200.estimated_spoilage_quantity == 0

    estimate_300 = material_estimate.estimates[2]
    assert estimate_300.order_quantity == 300
    assert estimate_300.material_quantity == 100
    assert estimate_300.estimated_stock_quantity == 7500
    assert estimate_300.spoilage_rate == 0
    assert estimate_300.estimated_spoilage_quantity == 0


def test_material_estimate__with_machine(db, carbonless_item, gto_machine):
    product = Product.objects.create(name='Carbonless Form')
    component = Component.objects.create_component(name='Sheets', type=Item.PAPER,
        product=product, machine=gto_machine, quantity=100,
        width_value=4, length_value=5, size_uom='inch')
    sheet_material = Material.objects.create_material(
        component=component, type=Item.PAPER, item=carbonless_item)

    material_estimate = sheet_material.estimate([75], 30, True)

    assert material_estimate is not None 
    assert material_estimate.estimates is not None
    assert len(material_estimate.estimates) == 1

    estimate = material_estimate.estimates[0]
    assert estimate.total_material_measures is not None

    assert estimate.output_per_item == 44
    assert estimate.estimated_stock_quantity == 171
    assert estimate.estimated_spoilage_quantity == 52
    assert estimate.estimated_total_quantity == 223

    raw_material_quantity = estimate.raw_material_measures.get(CostingMeasure.QUANTITY)
    raw_material_area = estimate.raw_material_measures.get(CostingMeasure.AREA)
    raw_material_perimeter = estimate.raw_material_measures.get(CostingMeasure.PERIMETER)
    assert raw_material_quantity is not None and \
        raw_material_area is not None and \
        raw_material_perimeter is not None
    assert raw_material_quantity.pc == 223
    assert math.isclose(raw_material_area.sq_inch, 212296)
    assert raw_material_perimeter.inch == 13826

    total_material_quantity = estimate.total_material_measures.get(CostingMeasure.QUANTITY)
    total_material_area = estimate.total_material_measures.get(CostingMeasure.AREA)
    total_material_perimeter = estimate.total_material_measures.get(CostingMeasure.PERIMETER)
    assert total_material_quantity is not None and \
        total_material_area is not None and \
        total_material_perimeter is not None
    assert total_material_quantity.pc == 7500
    assert math.isclose(total_material_area.sq_inch, 150000)
    assert total_material_perimeter.inch == 67500

    set_material_quantity = estimate.set_material_measures.get(CostingMeasure.QUANTITY)
    set_material_area = estimate.set_material_measures.get(CostingMeasure.AREA)
    set_material_perimeter = estimate.set_material_measures.get(CostingMeasure.PERIMETER)
    assert set_material_quantity is not None and \
        total_material_area is not None and \
        total_material_perimeter is not None
    assert set_material_quantity.pc == 75
    assert math.isclose(set_material_area.sq_inch, 1500)
    assert set_material_perimeter.inch == 675

    machine_run_quantity = estimate.machine_run_measures.get(CostingMeasure.QUANTITY)
    machine_run_area = estimate.machine_run_measures.get(CostingMeasure.AREA)
    machine_run_perimeter = estimate.machine_run_measures.get(CostingMeasure.PERIMETER)
    assert machine_run_quantity is not None and \
        machine_run_area is not None and \
        machine_run_perimeter is not None
    assert machine_run_quantity.pc == 892
    assert math.isclose(machine_run_area.sq_inch, 212296)
    assert machine_run_perimeter.inch == 27652

    assert estimate.raw_to_running_cut == 2
    assert estimate.running_to_final_cut == 9


def test_material_estimate__without_machine(db, carbonless_item):
    product = Product.objects.create(name='Carbonless Form')
    component = Component.objects.create_component(name='Sheets', type=Item.PAPER,
        product=product, quantity=100, width_value=4, length_value=5, size_uom='inch')
    sheet_material = Material.objects.create_material(
        component=component, type=Item.PAPER, item=carbonless_item)
    material_estimate = sheet_material.estimate([75], 30, True)

    assert material_estimate is not None 
    assert material_estimate.estimates is not None
    assert len(material_estimate.estimates) == 1

    estimate = material_estimate.estimates[0]

    raw_material_quantity = estimate.raw_material_measures.get(CostingMeasure.QUANTITY)
    raw_material_area = estimate.raw_material_measures.get(CostingMeasure.AREA)
    raw_material_perimeter = estimate.raw_material_measures.get(CostingMeasure.PERIMETER)
    assert raw_material_quantity is not None and \
        raw_material_area is not None and \
        raw_material_perimeter is not None
    assert raw_material_quantity.pc == 208
    assert math.isclose(raw_material_area.sq_inch, 198016)
    assert math.isclose(raw_material_perimeter.inch, 12896)

    total_material_quantity = estimate.total_material_measures.get(CostingMeasure.QUANTITY)
    total_material_area = estimate.total_material_measures.get(CostingMeasure.AREA)
    total_material_perimeter = estimate.total_material_measures.get(CostingMeasure.PERIMETER)
    assert total_material_quantity is not None and \
        total_material_area is not None and \
        total_material_perimeter is not None
    assert total_material_quantity.pc == 7500
    assert math.isclose(total_material_area.sq_inch, 150000)
    assert total_material_perimeter.inch == 67500

    set_material_quantity = estimate.set_material_measures.get(CostingMeasure.QUANTITY)
    set_material_area = estimate.set_material_measures.get(CostingMeasure.AREA)
    set_material_perimeter = estimate.set_material_measures.get(CostingMeasure.PERIMETER)
    assert set_material_quantity is not None and \
        total_material_area is not None and \
        total_material_perimeter is not None
    assert set_material_quantity.pc == 75
    assert math.isclose(set_material_area.sq_inch, 1500)
    assert set_material_perimeter.inch == 675

    machine_run_quantity = estimate.machine_run_measures.get(CostingMeasure.QUANTITY)
    machine_run_area = estimate.machine_run_measures.get(CostingMeasure.AREA)
    machine_run_perimeter = estimate.machine_run_measures.get(CostingMeasure.PERIMETER)
    assert machine_run_quantity is not None and \
        machine_run_area is not None and \
        machine_run_perimeter is not None
    assert machine_run_quantity.pc == 9776
    assert math.isclose(machine_run_area.sq_inch, 195520)
    assert machine_run_perimeter.inch == 87984

    assert estimate.output_per_item == 47
    assert estimate.estimated_stock_quantity == 160
    assert estimate.estimated_spoilage_quantity == 48
    assert estimate.estimated_total_quantity == 208

    assert estimate.raw_to_running_cut == 0
    assert estimate.running_to_final_cut == 0
    assert estimate.raw_to_final_cut == 15


def test_service__estimate(db, product_template):
    product_estimate = ProductEstimate.objects.create_product_estimate(
        product_template, [100])
    product = product_estimate.product
    assert len(product.services.all()) == 2

    print_service = product.services.filter(name='Printing').first()
    print_service_estimate = print_service.estimates
    assert print_service_estimate.operation_estimates is not None
    assert len(print_service_estimate.operation_estimates) == 3

    for operation_estimate in print_service_estimate.operation_estimates:
        assert operation_estimate.name == 'Front Print'
        assert operation_estimate.item_name in \
            ['Carbonless White', 'Carbonless Blue', 'Carbonless Yellow']
        assert operation_estimate.activity_estimates is not None
        assert len(operation_estimate.activity_estimates) == 2

        for activity_estimate in operation_estimate.activity_estimates:
            assert activity_estimate.name == 'Spot Color Printing'
            assert activity_estimate.notes in ['1st color', '2nd color'] 
            assert activity_estimate.activity_expense_estimates is not None
            assert len(activity_estimate.activity_expense_estimates) == 3

            electricity_expense = activity_estimate.activity_expense_estimates[2]
            assert electricity_expense.name == 'Electricity'
            assert electricity_expense.rate_label == '₱100.00 / hr'
            assert electricity_expense.estimates is not None
            assert len(electricity_expense.estimates) == 1
            electricity_expense_estimate = electricity_expense.estimates[0]
            assert electricity_expense_estimate is not None
            assert electricity_expense_estimate.order_quantity == 100
            assert electricity_expense_estimate.uom == 'hr'
            assert electricity_expense_estimate.type == 'hour'
            assert electricity_expense_estimate.rate.amount == 100
            assert electricity_expense_estimate.quantity == 2.25
            assert electricity_expense_estimate.duration.hr == 2.25
            assert electricity_expense_estimate.cost.amount == 225

            ink_expense = activity_estimate.activity_expense_estimates[1]
            assert ink_expense.name == 'Ink'
            assert ink_expense.rate_label == '₱0.75 / sheet'
            assert ink_expense.estimates is not None
            assert len(ink_expense.estimates) == 1
            ink_expense_estimate = ink_expense.estimates[0]
            assert ink_expense_estimate is not None
            assert ink_expense_estimate.order_quantity == 100
            assert ink_expense_estimate.uom == 'sheet'
            assert ink_expense_estimate.type == 'measure'
            assert ink_expense_estimate.rate.amount == 0.75
            assert ink_expense_estimate.quantity == 2500
            assert ink_expense_estimate.duration.hr == 2.25
            assert ink_expense_estimate.cost.amount == 1875

            depreciation_expense = activity_estimate.activity_expense_estimates[0]
            assert depreciation_expense.name == 'Depreciation'
            assert depreciation_expense.rate_label == '₱200.00 / hr'
            assert depreciation_expense.estimates is not None
            assert len(depreciation_expense.estimates) == 1
            depreciation_expense_estimate = depreciation_expense.estimates[0]
            assert depreciation_expense_estimate is not None
            assert depreciation_expense_estimate.order_quantity == 100
            assert depreciation_expense_estimate.uom == 'hr'
            assert depreciation_expense_estimate.type == 'hour'
            assert depreciation_expense_estimate.rate.amount == 200
            assert depreciation_expense_estimate.quantity == 2.25
            assert depreciation_expense_estimate.duration.hr == 2.25
            assert depreciation_expense_estimate.cost.amount == 450

    gathering_service = product.services.filter(name='Gathering').first()
    gathering_service_estimate = gathering_service.estimates
    assert gathering_service_estimate.operation_estimates is not None    
    assert len(gathering_service_estimate.operation_estimates) == 1

    gathering_operation_estimate = gathering_service_estimate.operation_estimates[0]
    assert gathering_operation_estimate.item_name is None
    assert gathering_operation_estimate.activity_estimates is not None
    assert len(gathering_operation_estimate.activity_estimates) == 1

    gathering_activity_estimate = gathering_operation_estimate.activity_estimates[0]
    assert gathering_activity_estimate.name == 'Gathering'
    assert gathering_activity_estimate.notes is None
    assert gathering_activity_estimate.activity_expense_estimates is not None
    assert len(gathering_activity_estimate.activity_expense_estimates) == 2

    labor_expense = gathering_activity_estimate.activity_expense_estimates[0]
    assert labor_expense.name == 'Labor'
    assert labor_expense.rate_label == '₱75.00 / hr'
    assert labor_expense.estimates is not None
    assert len(labor_expense.estimates) == 1
    labor_expense_estimate = labor_expense.estimates[0]
    assert labor_expense_estimate is not None
    assert labor_expense_estimate.order_quantity == 100
    assert labor_expense_estimate.uom == 'hr'
    assert labor_expense_estimate.type == 'hour'
    assert labor_expense_estimate.rate.amount == 75
    assert labor_expense_estimate.quantity == 2.06
    assert labor_expense_estimate.duration.hr == 2.06
    assert math.isclose(labor_expense_estimate.cost.amount, 154.5)


def test_product_estimate__set_material_spoilage_rate(db, product_template):
    product_estimate = ProductEstimate.objects.create_product_estimate(
        product_template, [100])
    product_estimate.set_material_spoilage_rate(10)
    product = product_estimate.product

    assert product_estimate.material_spoilage_rate == 10

    for component in product.components.all():
        for material in component.materials.all():
            assert material.spoilage_rate == 10


def test_product__estimate_total_prices_map(db, product_template):
    product_estimate = ProductEstimate.objects.create_product_estimate(
        product_template, [100,200,300])
    product = product_estimate.product

    assert product_estimate.estimates.total_prices_map is not None
    assert len(product_estimate.estimates.total_prices_map.items()) == 3

    # Material Totals
    material_estimates = product_estimate.estimates.material_estimates

    for estimate in material_estimates:
        assert estimate.total_prices_map is not None
        assert len(estimate.total_prices_map.items()) == 3

    # Service Totals
    print_service = product.services.filter(name='Printing').first()
    print_service_estimate = print_service.estimates

    assert print_service_estimate.total_prices_map is not None
    assert len(print_service_estimate.total_prices_map.items()) == 3

    for operation_estimate in print_service_estimate.operation_estimates:
        assert operation_estimate.total_prices_map is not None
        assert len(operation_estimate.total_prices_map.items()) == 3


def test_product_estimate_output_json(db, product_template):
    start_time = time.time()
    product_estimate = ProductEstimate.objects.create_product_estimate(
        product_template, [100, 200, 300, 400, 500])
    duration = time.time() - start_time
    print('created', duration)
    
    es = time.time()
    estimates = product_estimate.estimates
    assert estimates is not None
    duration = (time.time() - es)
    print('estimated', duration)

    ss = time.time()
    serializer = serializers.ProductEstimateEstimatesSerializer(estimates)
    assert serializer.data is not None
    duration = time.time() - ss
    print('serialized', duration)

    print('runtime', time.time() - start_time)
    assert duration <= 1.5


def test_product_service__input_measure(db):
    product_estimate = ProductEstimate.objects.create()
    product_estimate.set_estimate_quantities([100,200,300])
    product = Product.objects.create(name='Form', description='This is a sample form',
        product_estimate=product_estimate)
    
    service = Service.objects.create(name='Test Service', product=product, 
        input_quantity=500, input_uom='sheet')
    operation = OperationEstimate.objects.create(name='Test Operation', service=service)

    assert service.input_measure is not None
    assert service.input_measure.sheet == 500