import {AXIOS} from '@/utils/apis/core.js'

export class MetaProductApi {
    static uri = '/estimation/api/metaproducts'

    static async listMetaProducts(limit=null, offset=null, search=null) {
        const params = offset != null && limit != null? 
            {limit, offset, search} : {search};
        const response = await AXIOS.execute(AXIOS.GET, MetaProductApi.uri,
            null, null, null, params);
        if (response) return response.data;
    }

    static async createMetaProduct(metaProduct) {
        const response = await AXIOS.execute(AXIOS.POST, 
            MetaProductApi.uri, 'Product Meta created successfully.', 
            'Create failed. Please try again.', metaProduct);
        return response;
    }

    static async retrieveMetaProduct(id) {
        const response = await AXIOS.execute(AXIOS.GET, MetaProductApi.uri + `/${id}/`)
        return response.data
    }

    static async updateMetaProduct(id, metaProduct) {
        const response = await AXIOS.execute(AXIOS.PUT, 
            MetaProductApi.uri + `/${id}/`, 'Product Meta updated successfully.', 
            'Update failed. Please try again.', metaProduct)
        if (response) return response.data;
    }

    static async deleteMetaProduct(id) {
        await AXIOS.execute(AXIOS.DELETE, MetaProductApi.uri + `/${id}/`, 
            'Product Meta deleted successfully.', 'Delete failed. Please try again.');
    }

    static async retrieveMetaProductComponents(id, getOptions=false) {
        const action = (getOptions)? AXIOS.OPTIONS : AXIOS.GET;
        const response = await AXIOS.execute(action, 
            MetaProductApi.uri + `/${id}/metacomponents`);
        if (response) return response.data;
    }

    static async createMetaProductComponent(id, metaComponent) {
        const response = await AXIOS.execute(AXIOS.POST, 
            MetaProductApi.uri + `/${id}/metacomponents`, 
            'Component created successfully.', 'Create failed. Please try again.', 
            metaComponent);
        return response;
    }

    static async retrieveMetaProductServices(id, getOptions=false) {
        const action = (getOptions)? AXIOS.OPTIONS : AXIOS.GET;
        const response = await AXIOS.execute(action, 
            MetaProductApi.uri + `/${id}/metaservices`);
        if (response) return response.data;
    }

    static async createMetaProductService(id, metaService) {
        const response = await AXIOS.execute(AXIOS.POST, 
            MetaProductApi.uri + `/${id}/metaservices`, 
            'Service created successfully.', 'Create failed. Please try again.', 
            metaService);
        return response;
    }

    static async updateMetaServiceSequence(id, serviceSequences) {
        const response = await AXIOS.execute(AXIOS.PUT, 
            MetaProductApi.uri + `/${id}/metaservices/sequences`, null, 
            null, serviceSequences)
        if (response) return response.data;
    }
}


export class MetaComponentApi {
    static uri = '/estimation/api/metacomponents'

    static async retrieveMetaComponent(id) {
        const response = await AXIOS.execute(AXIOS.GET, MetaComponentApi.uri + `/${id}/`)
        return response.data
    }

    static async updateMetaComponent(id, metaComponent) {
        const response = await AXIOS.execute(AXIOS.PUT, 
            MetaComponentApi.uri + `/${id}/`, 'Component updated successfully.', 
            'Update failed. Please try again.', metaComponent)
        if (response) return response.data;
    }

    static async deleteMetaComponent(id) {
        await AXIOS.execute(AXIOS.DELETE, MetaComponentApi.uri + `/${id}/`, 
            'Component deleted successfully.', 'Delete failed. Please try again.');
    }

}


export class MetaServiceApi {
    static uri = '/estimation/api/metaservices'

    static async retrieveMetaService(id) {
        const response = await AXIOS.execute(AXIOS.GET, MetaServiceApi.uri + `/${id}/`)
        return response.data
    }

    static async updateMetaService(id, metaService) {
        const response = await AXIOS.execute(AXIOS.PUT, 
            MetaServiceApi.uri + `/${id}/`, 'Service updated successfully.', 
            'Update failed. Please try again.', metaService)
        if (response) return response.data;
    }

    static async deleteMetaService(id) {
        await AXIOS.execute(AXIOS.DELETE, MetaServiceApi.uri + `/${id}/`, 
            'Component deleted successfully.', 'Delete failed. Please try again.');
    }

}