import pandas as pd
from cached_property import cached_property
from inventory.models import Item


class ItemSheet:

    def __init__(self, name, objects=[]):
        self.name = name
        self.objects = objects

    @property
    def headers(self):
        return ['Id', 'Item Name', 'Base Unit', 'Alternate Unit', 'Price per Unit']

    @cached_property
    def rows(self):
        rows = []
        if self.objects is not None and len(self.objects) > 0:
            for paper in self.objects:
                row = self.get_row(paper)
                rows.append(row)
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
                    ("Row #%s does not expected column count of %s." % 
                        (index, expected_column_count))
        else:
            assert row_count > 0, "Rows must not be empty."

    def write_excel(self, writer):
        dataframe = self.dataframe
        dataframe.to_excel(writer, sheet_name=self.name)
    
    def get_row(self, obj):
        id = obj.id
        name = obj.name
        base_unit = obj.base_uom.name
        alternate_unit = obj.alternate_uom.name
        price = obj.properties.override_price
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