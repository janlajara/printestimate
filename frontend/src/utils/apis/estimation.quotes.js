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
        return response.data;
    }

    static async updateEstimate(id, estimate) {
        const response = await AXIOS.execute(AXIOS.PUT, 
            EstimateApi.uri + `/${id}/`, 'Estimate updated successfully.', 
            'Update failed. Please try again.', estimate)
        if (response) return response.data;
    }

    static async retrieveEstimate(id) {
        const response = await AXIOS.execute(AXIOS.GET, EstimateApi.uri + `/${id}/`)
        return response.data
    }

    static async retrieveEstimateCosts(id) {
        const response = await AXIOS.execute(AXIOS.GET, EstimateApi.uri + `/${id}/costs`)
        return response.data
    }

    static async deleteEstimate(id) {
        await AXIOS.execute(AXIOS.DELETE, EstimateApi.uri + `/${id}/`, 
            'Estimate deleted successfully.', 'Delete failed. Please try again.');
    }
    
}