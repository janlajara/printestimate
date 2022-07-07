from datetime import datetime
from rest_framework.views import APIView
from fileio.inventory.models import ItemWorkbook
from fileio.models import BytesExcelWriter
from fileio import constants
from django.http import FileResponse


class ItemsWorkbookView(APIView):

    def get(self, request):
        file_name = 'items-workbook_%s' % datetime.now().strftime(
            constants.FILE_TIMESTAMP_PATTERN)
        items_workbook = ItemWorkbook(name=file_name)
        output = BytesExcelWriter.write(items_workbook)

        file_content = output
        file_response = FileResponse(file_content, 
            content_type=constants.HTTP_CONTENT_TYPE_EXCEL_FILE,
            as_attachment=True, filename=items_workbook.filename)

        return file_response