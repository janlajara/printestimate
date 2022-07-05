import pandas as pd
import pytest
from inventory.models import Item, BaseStockUnit, AlternateStockUnit
from estimation.template.tests import meta_product, gto_workstation, \
    gto_machine, finishing_workstation
from estimation.product.models import ProductEstimate
from estimation.product.tests import product_template
from fileio.estimation.models import CostEstimateWorkbook


@pytest.fixture
def item_factory(db):
    def create_item(**kwargs):
        buom = BaseStockUnit.objects.create(name='sheet', abbrev='sht')
        auom = AlternateStockUnit.objects.create(name='ream', abbrev='rm')
        auom.base_stock_units.add(buom)
        item = Item.objects.create_item(base_uom=buom, alternate_uom=auom, 
                                        override_price=3, **kwargs)
        return item
    return create_item


@pytest.fixture
def product(db, product_template):
    product_estimate = ProductEstimate.objects.create_product_estimate(
        product_template)
    product_estimate.set_estimate_quantities([100, 200, 300])
    return product_estimate


def test_product_summary_sheet(db, product):
    workbook = CostEstimateWorkbook(product, 'estimate-workbook')

    assert workbook.sheets is not None
    summary_sheet = workbook.sheets[0]
    assert summary_sheet is not None
    assert summary_sheet.general_information_section is not None
    assert summary_sheet.component_section is not None
    assert summary_sheet.service_section is not None

    gen_info_section = summary_sheet.general_information_section
    assert gen_info_section.code == 'CE-0001'
    assert gen_info_section.name == 'Forms'
    assert gen_info_section.description == '8.5x11" Form'

    component_section = summary_sheet.component_section
    assert len(component_section.rows) == 1
    assert component_section.start_row == 4
    assert component_section.start_col == 0

    service_section = summary_sheet.service_section
    assert len(service_section.rows) == 7
    assert service_section.start_row == 7
    assert service_section.start_col == 0

    path_to_file = 'test_write_excel.xlsx'
    with pd.ExcelWriter(path_to_file, engine='xlsxwriter') as writer:
        workbook.write(writer)