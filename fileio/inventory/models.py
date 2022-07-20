import pandas as pd
from cached_property import cached_property
from inventory.models import Item
from fileio import constants
from fileio.models import ExcelWorkbook


class ItemSheet:

    def __init__(self, name, objects=[]):
        self.name = name
        self.objects = objects

    @property
    def headers(self):
        return ['Id', 'Item Name', 'Base Unit', 'Alternate Unit', 'Price/Base Unit']

    @cached_property
    def rows(self):
        rows = []
        if self.objects is not None and len(self.objects) > 0:
            for paper in self.objects:
                row = self.get_row(paper)
                rows.append(row)
        else:
            # Create an empty row as workaround for table formatting requirement
            rows = [[''] * len(self.headers)]
        return rows

    @cached_property
    def dataframe(self):
        self._validate()
        dataframe = pd.DataFrame(self.rows, columns=self.headers)
        dataframe.set_index('Id', inplace=True)
        return dataframe

    def _validate(self):
        row_count = len(self.rows)
        if row_count > 0:
            expected_column_count = len(self.headers)
            for index, row in enumerate(self.rows):
                actual_column_count = len(row)
                assert actual_column_count == expected_column_count, \
                    ("Row #%s does not match expected column count of %s." % 
                        (index, expected_column_count))

    def write(self, writer):
        dataframe = self.dataframe
        dataframe.to_excel(writer, sheet_name=self.name)
        self.format(writer)

    def format(self, writer):
        workbook = writer.book
        money_format = workbook.add_format({'num_format': constants.CURRENCY_FORMAT})

        # Format column width and types
        worksheet = writer.sheets[self.name]
        if worksheet is not None:
            worksheet.set_column(1, 1, 30)
            worksheet.set_column(2, 4, 15)
            worksheet.set_column(4, 4, None, money_format)

        # Turn into a formatted table
        (max_row, max_col) = self.dataframe.shape
        if max_row > 0:
            column_settings = [{'header': column} for column in self.headers]
            worksheet.add_table(0, 0, max_row, max_col, {'columns': column_settings})
    
    def get_row(self, obj):
        id = obj.id
        name = obj.name
        base_unit = obj.base_uom.name
        alternate_unit = (obj.alternate_uom.name if 
            obj.alternate_uom is not None else None)
        price = obj.override_price.amount
        return [id, name, base_unit, alternate_unit, price]


class LineSheet(ItemSheet):

    @property
    def headers(self):
        return super().headers + ['Length', 'Length Uom']

    def get_row(self, obj):
        row = super().get_row(obj)
        length = obj.properties.length_value
        uom = obj.properties.length_uom
        return row + [length, uom]


class TapeSheet(LineSheet):
    
    @property
    def headers(self):
        return super().headers + ['Width', 'Width Uom']

    def get_row(self, obj):
        row = super().get_row(obj)
        width = obj.properties.width_value
        uom = obj.properties.width_uom
        return row + [width, uom]


class PaperSheet(ItemSheet):

    @property
    def headers(self):
        return super().headers + ['Width', 'Length', 'Size Uom', 'Gsm', 'Finish']

    def get_row(self, obj):
        row = super().get_row(obj)
        width = obj.properties.width_value
        length = obj.properties.length_value
        size_uom = obj.properties.size_uom
        gsm = obj.properties.gsm
        finish = obj.properties.finish
        return row + [width, length, size_uom, gsm, finish]


class PanelSheet(PaperSheet):

    @property
    def headers(self):
        return super().headers + ['Thickness', 'Thickness Uom']

    def get_row(self, obj):
        row = super().get_row(obj)
        thickness = obj.properties.thickness_value
        uom = obj.properties.thickness_uom
        return row + [thickness, uom]


class LiquidSheet(ItemSheet):
    
    @property
    def headers(self):
        return super().headers + ['Volume', 'Volume Uom']

    def get_row(self, obj):
        row = super().get_row(obj)
        volume = obj.properties.volume_value
        uom = obj.properties.volume_uom
        return row + [volume, uom]


class ItemWorkbook(ExcelWorkbook):
    def __init__(self, name='items-workbook'):
        self.name = name

    @property
    def sheets(self):
        sheets = []

        for item_type in Item.TYPES:
            type = item_type[0]
            items = self._get_items_by_type(type)
            worksheet = ItemSheet(name=type, objects=items)
            sheets.append(worksheet)
        
        return sheets

    def _get_items_by_type(self, type):
        return Item.objects.filter(type=type).order_by('name').all()