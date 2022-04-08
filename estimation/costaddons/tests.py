import pytest
from estimation.product.models import ProductEstimate
from estimation.costaddons.models import ConfigCostAddon, ConfigCostAddonOption, \
    TemplateCostAddonSet, TemplateCostAddonItem, EstimateAddonSet, EstimateAddonItem


@pytest.fixture
def create_config_cost_addon(db):
    def _create(**kwargs):
        return ConfigCostAddon.objects.create(**kwargs)
    return _create


@pytest.fixture
def create_template_cost_addon_set(db):
    def _create(**kwargs):
        return TemplateCostAddonSet.objects.create(**kwargs)
    return _create


@pytest.fixture
def create_estimate_addon_set(db):
    def _create(**kwargs):
        return EstimateAddonSet.objects.create(**kwargs)
    return _create


def test_config_cost_addon__symbol(db, create_config_cost_addon):
    vat_addon = create_config_cost_addon(name='VAT', 
        type=ConfigCostAddon.PERCENTAGE)
    delivery_addon = create_config_cost_addon(name='Delivery',
        type=ConfigCostAddon.FLAT)
    
    assert vat_addon.symbol == '%' 
    assert delivery_addon.symbol == 'PHP'


def test_config_cost_addon__options(db, create_config_cost_addon):
    delivery_addon = create_config_cost_addon(name='Delivery Fee',
        type=ConfigCostAddon.FLAT)
    manila_delivery = delivery_addon.add_option(1000, 'Manila')
    starosa_delivery = delivery_addon.add_option(500, 'Sta. Rosa')
    calamba_delivery = delivery_addon.add_option(300, 'Calamba') 

    assert delivery_addon.has_options
    assert manila_delivery is not None
    assert manila_delivery.formatted_value == '1000 PHP'
    
    assert starosa_delivery is not None
    assert starosa_delivery.formatted_value == '500 PHP'

    assert calamba_delivery is not None
    assert calamba_delivery.formatted_value == '300 PHP'


def test_template_cost_addon_set__set_default(db, create_config_cost_addon, 
        create_template_cost_addon_set):
    regular_template = create_template_cost_addon_set(name='Regular', is_default=True)
    custom_template = create_template_cost_addon_set(name='Custom')
    another_template = create_template_cost_addon_set(name='Another')
    another_template.set_default()

    regular_template.refresh_from_db()

    assert not regular_template.is_default
    assert not custom_template.is_default
    assert another_template.is_default


def test_template_cost_addon_set__add_item(db, create_config_cost_addon, 
        create_template_cost_addon_set):
    delivery_addon = create_config_cost_addon(name='Delivery Fee',
        type=ConfigCostAddon.FLAT)
    delivery_addon.add_option(1000, 'Manila')
    delivery_addon.add_option(500, 'Sta. Rosa')
    delivery_addon.add_option(300, 'Calamba')

    sales_tax_addon = create_config_cost_addon(name='Sales Tax',
        type=ConfigCostAddon.PERCENTAGE)
    sales_tax_addon.add_option(12, 'VAT')
    sales_tax_addon.add_option(0, 'Non-VAT')
    sales_tax_addon.add_option(0, 'Zero-rated')

    regular_template = create_template_cost_addon_set(name='Regular', is_default=True)
    delivery_template_item = regular_template.add_item(delivery_addon)
    salestax_template_item = regular_template.add_item(sales_tax_addon)

    assert len(regular_template.template_cost_addon_items.all()) == 2
    assert delivery_template_item is not None and delivery_template_item.sequence == 1 
    assert salestax_template_item is not None and salestax_template_item.sequence == 2


def test_estimate_addon_set__add_addon_item(db, create_estimate_addon_set):
    product_estimate = ProductEstimate.objects.create()
    assert hasattr(product_estimate, 'estimate_addon_set') == False
    
    addon_set = create_estimate_addon_set(product_estimate=product_estimate)
    delivery_fee = addon_set.add_addon_item('Delivery Fee', 1, 
        ConfigCostAddon.FLAT, value=500, allow_custom_value=True)

    assert product_estimate.estimate_addon_set is not None
    assert delivery_fee is not None
    assert len(addon_set.estimate_addon_items.all()) == 1


def test_estimate_addon_set__get_addon_costs(db, create_estimate_addon_set):
    product_estimate = ProductEstimate.objects.create()
    addon_set = create_estimate_addon_set(product_estimate=product_estimate)
    delivery_fee = addon_set.add_addon_item('Delivery Fee', 1, 
        ConfigCostAddon.FLAT, value=500, allow_custom_value=True)
    sales_tax = addon_set.add_addon_item('Sales Tax', 2, ConfigCostAddon.PERCENTAGE, value=12)

    addon_costs = addon_set.get_addon_costs(1000)
    expected_costs = [500, 180]

    for index, addon_cost in enumerate(addon_costs):
        assert addon_cost.addon_cost == expected_costs[index]

    cost_set = addon_set.get_addon_cost_set(50, 1000)
    assert cost_set.order_quantity == 50
    assert len(cost_set.addon_costs) == 2

        