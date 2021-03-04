import {useToast} from 'vue-toastification'

const toast = useToast();
const showToast = (type='default', message=null)=> {
    if (message != null)
        return toast(message, {type});
}
const toastResponse = (response, success, error)=> {
    if (response.status == 200) {
        showToast("success", success);
    } else {
        showToast("error", error);
        console.error(response);
    }
};

const _axios = require('axios')
const API_HOSTNAME = 'http://localhost:8000'
const AXIOS =  {
    execute: async (method, uri, success, error, data)=> {
        const methods = ["post", "put", "get"];
        const url = API_HOSTNAME + uri;
        const config = {
            url: url,
            method: methods[method],
            data
        }
        let response;

        try {
            response = await _axios.request(config);
            if (success != null && error != null)
                toastResponse(response, success, error);
        } catch (err) {
            showToast('error', 'Failed to reach the server. Please try again.')
            console.error(err);
        }
        return response;
    },
    POST: 0,
    PUT: 1,
    GET: 2,
}


export class InventoryApi {
    static uri = '/inventory/api/item'

    static async createItem(item) {
        const response = await AXIOS.execute(AXIOS.POST, InventoryApi.uri, item);
        return response
    }

    static async listItems() {
        const response = await AXIOS.execute(AXIOS.GET, InventoryApi.item_uri);
        return response.data;
    }
}

export class BaseStockUnitApi {
    static uri = '/inventory/api/basestockunit'

    static async listBaseStockUnits() {
        const response = await AXIOS.execute(AXIOS.GET, BaseStockUnitApi.uri);
        return response.data;
    }

    static async retrieveBaseStockUnit(id) {
        const response = await AXIOS.execute(AXIOS.GET, BaseStockUnitApi.uri + `/${id}`)
        return response.data
    }

    static async updateBaseStockUnit(id, baseStockUnit) {
        const response = await AXIOS.execute(AXIOS.PUT, BaseStockUnitApi.uri + `/${id}/`, 
            'Stock unit updated successfully', 'Update failed. Please try again.', baseStockUnit
        )
        if (response) return response.data;
    }
}

export class AlternateStockUnitApi {
    static uri = '/inventory/api/alternatestockunit'

    static async listAlternateStockUnits() {
        const response = await AXIOS.execute(AXIOS.GET, AlternateStockUnitApi.uri);
        return response.data;
    }
}
