from io import BytesIO
import pandas as pd
from abc import ABC, abstractmethod

class BytesExcelWriter:

    @classmethod
    def write(cls, workbook):
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            workbook.write(writer)
        output.seek(0)
        return output


class ExcelWorkbook(ABC):
    def __init__(self, name='workbook'):
        self.name = name
    
    @property
    def filename(self):
        return '%s.%s' % (self.name, constants.FILE_EXTENSION_EXCEL)

    @property
    @abstractmethod
    def sheets(self):
        pass

    def write(self, writer):
        for sheet in self.sheets:
            sheet.write(writer)