from django.shortcuts import get_object_or_404
from datetime import datetime
from estimation.product.models import ProductEstimate
from fileio.estimation.models import CostEstimateWorkbook
from fileio.models import BytesExcelWriter
from fileio import constants
from rest_framework.views import APIView, status
from django.http import FileResponse
from rest_framework.response import Response

class CostEstimateView(APIView):

    def get(self, request, *args, **kwargs):
        if 'pk' in kwargs:

            pk = self.kwargs['pk']
            product_estimate = get_object_or_404(ProductEstimate, pk=pk)
            file_name = 'cost-estimate-workbook_%s' % datetime.now().strftime(
                constants.FILE_TIMESTAMP_PATTERN)
            workbook = CostEstimateWorkbook(product_estimate, file_name)
            output = BytesExcelWriter.write(workbook)

            file_content = output
            file_response = FileResponse(file_content, 
                content_type=constants.HTTP_CONTENT_TYPE_EXCEL_FILE,
                as_attachment=True, filename=workbook.filename)
            return file_response
        
        return Response({'error': "'pk' must be provided as a request parameter."}, 
            status.HTTP_400_BAD_REQUEST)