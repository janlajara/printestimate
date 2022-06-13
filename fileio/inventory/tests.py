import pandas as pd
import pytest
import io
from inventory.models import Item, BaseStockUnit, AlternateStockUnit
from fileio.inventory.models import PaperSheet, ItemWorkbook
from fileio.models import BytesExcelWriter


@pytest.fixture
def base_unit__sheet(db):
    return BaseStockUnit.objects.create(name='sheet', abbrev='sht')

@pytest.fixture
def alt_unit__ream(db, base_unit__sheet):
    alt_stock_unit = AlternateStockUnit.objects.create(name='ream', abbrev='rm')
    alt_stock_unit.base_stock_units.add(base_unit__sheet)
    return alt_stock_unit

@pytest.fixture
def item_factory(db, base_unit__sheet: BaseStockUnit, alt_unit__ream: AlternateStockUnit):
    def create_item(**data):
        item = Item.objects.create_item(base_uom=base_unit__sheet,
                                        alternate_uom=alt_unit__ream,
                                        **data)
        return item
    return create_item

def test_itemsheet__write_excel(db, item_factory):
    path_to_file = 'test_write_excel.xlsx'
    paper_items = []

    item = item_factory(type=Item.PAPER, name='Carbonless White')
    item.properties.length_value = 22
    item.properties.width_value = 34
    item.properties.size_uom = 'inch'
    item.override_price = 25.00
    paper_items.append(item)

    item = item_factory(type=Item.PAPER, name='Carbonless Yellow')
    item.properties.length_value = 22
    item.properties.width_value = 34
    item.properties.size_uom = 'inch'
    item.override_price = 25.00
    paper_items.append(item)

    paper_sheet = PaperSheet(Item.PAPER, objects=paper_items)

    assert len(paper_sheet.rows) == 2
    assert paper_sheet.dataframe is not None

    #with pd.ExcelWriter(path_to_file, engine='xlsxwriter') as writer:
    #    paper_sheet.write(writer)


def test_item_workbook__get_sheets(db, item_factory):
    paper = item_factory(type=Item.PAPER, name='Carbonless White')
    paper.properties.length_value = 22
    paper.properties.width_value = 34
    paper.properties.size_uom = 'inch'
    paper.override_price = 5.00
    paper.save()

    piece_uom = BaseStockUnit.objects.create(name='piece', abbrev='pc')
    panel = Item.objects.create_item(type=Item.PANEL, 
        name='Sintra Board', base_uom=piece_uom)
    panel.properties.length_value = 8
    panel.properties.width_value = 4
    panel.properties.size_uom = 'ft'
    panel.properties.thickness_value = 3
    panel.properties.thickness_uom = 'mm'
    panel.override_price = 400.00
    panel.save()

    other = Item.objects.create_item(type=Item.OTHER, 
        name='Calling Card Case', base_uom=piece_uom)
    other.override_price = 25.00
    other.save()

    workbook = ItemWorkbook(name='testwb.xlsx')
    assert workbook.sheets is not None
    assert len(workbook.sheets) >= 3

    #path_to_file = 'test_write_excel.xlsx'
    #with pd.ExcelWriter(path_to_file, engine='xlsxwriter') as writer:
    #    workbook.write(writer)