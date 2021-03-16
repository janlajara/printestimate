import {useToast} from 'vue-toastification'

const toast = useToast();
const showToast = (type='default', message=null)=> {
    if (message != null)
        return toast(message, {type});
}
const toastResponse = (response, success, error)=> {
    if (response.status >= 200 && response.status <= 299) {
        if (success) showToast("success", success);
    } else {
        if (error) showToast("error", error);
        console.error(response);
    }
};

const _axios = require('axios')
const API_HOSTNAME = 'http://localhost:8000'
const AXIOS =  {
    execute: async (method, uri, success, error, data, params)=> {
        const methods = ["post", "put", "get", "delete", "options"];
        const url = API_HOSTNAME + uri;
        const config = {
            url: url,
            method: methods[method],
            data, params
        }; 
        let response; 

        try {
            response = await _axios.request(config);
            if (success != null || error != null)
                toastResponse(response, success, error);
        } catch (err) {
            showToast('error', 'An error occurred in the server. Please try again.')
            console.error(err);
        }
        return response;
    },
    POST: 0,
    PUT: 1,
    GET: 2,
    DELETE: 3,
    OPTIONS: 4,
}


export class ItemApi {
    static uri = '/inventory/api/item'

    static async getItemTypes() {
        const response = await AXIOS.execute(AXIOS.OPTIONS, ItemApi.uri);
        if (response.data && response.data.actions.POST) {
            return response.data.actions.POST.type.choices
        }
    }

    static async createItem(item) {
        const response = await AXIOS.execute(AXIOS.POST, ItemApi.uri, 
            'Item created successfully.', 'Create failed. Please try again.', item);
        return response;
    }

    static async listItems() {
        const response = await AXIOS.execute(AXIOS.GET, ItemApi.uri);
        if (response) return response.data;
    }

    static async retrieveItem(id) {
        const response = await AXIOS.execute(AXIOS.GET, ItemApi.uri + `/${id}`)
        return response.data
    }

    static async deleteItem(id) {
        await AXIOS.execute(AXIOS.DELETE, ItemApi.uri + `/${id}/`, 
            'Item deleted successfully.', 'Delete failed. Please try again.');
    }
}


export class ItemPropertiesApi {
    static uri = '/inventory/api/itemproperties'

    static async getItemProperties(itemType) {
        const response = await AXIOS.execute(AXIOS.OPTIONS, 
            ItemPropertiesApi.uri, null, null, null, {resourcetype: itemType});
        if (response.data && response.data.actions.POST)
            return response.data.actions.POST;
    }
}

export class BaseStockUnitApi {
    static uri = '/inventory/api/basestockunit'

    static async listBaseStockUnits() {
        const response = await AXIOS.execute(AXIOS.GET, BaseStockUnitApi.uri);
        return response.data;
    }

    static async createBaseStockUnit(baseStockUnit) {
        const response = await AXIOS.execute(AXIOS.POST, BaseStockUnitApi.uri,
            'Stock unit created successfully.', 'Create failed. Please try again.', baseStockUnit);
        return response.data;
    }

    static async deleteBaseStockUnit(id) {
        await AXIOS.execute(AXIOS.DELETE, BaseStockUnitApi.uri + `/${id}/`, 
            'Stock unit deleted successfully.', 'Delete failed. Please try again.');
    }

    static async retrieveBaseStockUnit(id) {
        const response = await AXIOS.execute(AXIOS.GET, BaseStockUnitApi.uri + `/${id}`)
        return response.data
    }

    static async updateBaseStockUnit(id, baseStockUnit) {
        const response = await AXIOS.execute(AXIOS.PUT, BaseStockUnitApi.uri + `/${id}/`, 
            'Stock unit updated successfully.', 'Update failed. Please try again.', baseStockUnit);
        if (response) return response.data;
    }
}

export class AlternateStockUnitApi {
    static uri = '/inventory/api/alternatestockunit'

    static async createAlternateStockUnit(baseStockUnit) {
        const response = await AXIOS.execute(AXIOS.POST, AlternateStockUnitApi.uri,
            'Stock unit created successfully.', 'Create failed. Please try again.', baseStockUnit);
        return response.data;
    }

    static async deleteAlternateStockUnit(id) {
        await AXIOS.execute(AXIOS.DELETE, AlternateStockUnitApi.uri + `/${id}/`, 
            'Stock unit deleted successfully.', 'Delete failed. Please try again.');
    }

    static async listAlternateStockUnits() {
        const response = await AXIOS.execute(AXIOS.GET, AlternateStockUnitApi.uri);
        return response.data;
    }

    static async retrieveAlternateStockUnit(id) {
        const response = await AXIOS.execute(AXIOS.GET, AlternateStockUnitApi.uri + `/${id}`)
        return response.data
    }

    static async updateAlternateStockUnit(id, alternateStockUnit) {
        const response = await AXIOS.execute(AXIOS.PUT, AlternateStockUnitApi.uri + `/${id}/`, 
            'Stock unit updated successfully.', 'Update failed. Please try again.', alternateStockUnit
        )
        if (response) return response.data;
    }
}
