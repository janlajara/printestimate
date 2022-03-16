import {AXIOS} from '@/utils/apis/core.js'

export class CostingMeasureUnitsApi {
    static uri = '/core/api/utils/costingmeasures/units'

    static async listUnits() {
        const response = await AXIOS.execute(AXIOS.GET, CostingMeasureUnitsApi.uri);
        if (response) return response.data;
    }
}