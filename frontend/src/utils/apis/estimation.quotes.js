import {AXIOS} from '@/utils/apis/core.js'

export class EstimateApi {
    static uri = '/estimation/api/products/estimates'

    static async listEstimates(limit, offset) {
        const params = {limit, offset}
        const response = await AXIOS.execute(AXIOS.GET, EstimateApi.uri,
            null, null, null, params);
        if (response) return response.data;
    }
    
    static async createEstimate(estimate) {
        const response = await AXIOS.execute(AXIOS.POST, 
            EstimateApi.uri, 'Estimate created successfully.', 
            'Create failed. Please try again.', estimate);
        return response;
    }

    static async retrieveEstimate(id) {
        const response = await AXIOS.execute(AXIOS.GET, EstimateApi.uri + `/${id}/`)
        return response.data
    }

    
}