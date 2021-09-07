import {AXIOS} from '@/utils/apis/core.js'

export class ProductTemplateApi {
    static uri = '/estimation/api/templates/products'

    static async listProductTemplates() {
        const response = await AXIOS.execute(AXIOS.GET, ProductTemplateApi.uri);
        if (response) return response.data;
    }

    static async createProductTemplate(productTemplate) {
        const response = await AXIOS.execute(AXIOS.POST, 
            ProductTemplateApi.uri, 'Product Template created successfully.', 
            'Create failed. Please try again.', productTemplate);
        return response;
    }

    static async retrieveProductTemplate(id) {
        const response = await AXIOS.execute(AXIOS.GET, ProductTemplateApi.uri + `/${id}/`)
        return response.data
    }

    static async updateProductTemplate(id, productTemplate) {
        const response = await AXIOS.execute(AXIOS.PUT, 
            ProductTemplateApi.uri + `/${id}/`, 'Product Template updated successfully.', 
            'Update failed. Please try again.', productTemplate)
        if (response) return response.data;
    }
}

export class ComponentTemplateApi {
    static uri = '/estimation/api/templates/products/components'

    static async getComponentMetaData() {
        const response = await AXIOS.execute(AXIOS.GET, 
            ComponentTemplateApi.uri + '/metadata');
        return response;
    }
}