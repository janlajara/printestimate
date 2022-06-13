from io import BytesIO
import pandas as pd

class BytesExcelWriter:

    @classmethod
    def write(cls, workbook):
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            workbook.write(writer)
        output.seek(0)
        return output
