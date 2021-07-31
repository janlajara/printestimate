import {AXIOS} from '@/utils/apis/core.js'

export class MetaProductApi {
    static uri = '/estimation/api/metaproducts'

    static async listMetaProducts() {
        const response = await AXIOS.execute(AXIOS.GET, MetaProductApi.uri);
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