from rest_framework.views import APIView
from rest_framework.response import Response
from core import serializers
from core.utils.measures import CostingMeasure

class CostingMeasuresListView(APIView):

    def get(self, request, format=None):
        measures = CostingMeasure.get_all_measures()
        serializer = serializers.CostingMeasureSerializer(measures, many=True)
        return Response(serializer.data)