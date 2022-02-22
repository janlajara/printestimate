import {AXIOS} from '@/utils/apis/core.js'

export class ProductTemplateApi {
    static uri = '/estimation/api/templates/products'

    static async listProductTemplates(limit=null, offset=null, search=null) {
        const params = offset != null && limit != null? 
            {limit, offset, search} : {search};
        const response = await AXIOS.execute(AXIOS.GET, ProductTemplateApi.uri,
            null, null, null, params);
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

    static async deleteProductTemplate(id) {
        await AXIOS.execute(AXIOS.DELETE, ProductTemplateApi.uri + `/${id}/`, 
            'Template deleted successfully.', 'Delete failed. Please try again.');
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