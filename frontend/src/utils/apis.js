import {useToast} from 'vue-toastification'
import {reference} from '@/utils/format.js'

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
            let error = err.response.data;
            if (err.response.data.properties) {
                const errArr = [];
                Object.entries(err.response.data.properties).forEach(entry => {
                    errArr.push(`${entry[0]} : ${entry[1]}`)
                })
                error = errArr.join(', ');
            }
            return {
                error
            };
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
    static uri = '/inventory/api/items'

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

    static async updateItem(id, item) {
        const response = await AXIOS.execute(AXIOS.PUT, ItemApi.uri + `/${id}/`, 
            'Item updated successfully.', 'Update failed. Please try again.', item);
        return response;
    }

    static async listItems(limit, offset, search) {
        const params = offset != null && limit != null? 
            {limit, offset, search} : {search};
        const response = await AXIOS.execute(AXIOS.GET, ItemApi.uri,
            null, null, null, params);
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

    static async retrieveItemStockSummary(id) {
        const response = await AXIOS.execute(AXIOS.GET, ItemApi.uri + `/${id}/stocks`)
        return response.data
    }

    static async listItemStocks(id, limit, offset, availableOnly=false) {
        const params = offset != null && limit != null? 
            {limit, offset, "available-only": availableOnly} : null;
        const response = await AXIOS.execute(AXIOS.GET, ItemApi.uri + `/${id}/stocks/list`,
            null, null, null, params)
        return response.data
    }

    static async depositStock(id, stock) {
        const response = await AXIOS.execute(AXIOS.POST, ItemApi.uri + `/${id}/stocks/deposit`,
            'Stock deposited successfully.', 'Deposit failed. Please try again.', stock);
        return response.data
    }

    static async withdrawStocks(id, requests) {
        const response = await AXIOS.execute(AXIOS.POST, ItemApi.uri + `/${id}/stocks/withdraw`,
            null, 'Stock request failed. Please try again.', requests);
        if (response.data) {
            const requestId = reference.formatId(response.data.id, reference.stockRequestGroup)
            showToast("success", `Request ${requestId} has been created.`);
        }
        return response.data
    }

    static async listItemStockHistory(id, limit, offset) {
        const params = offset != null && limit != null? 
            {limit, offset} : null; 
        const response = await AXIOS.execute(AXIOS.GET, ItemApi.uri + `/${id}/stocks/history`,
            null, null, null, params)
        return response.data
    }

    static async listItemRequestGroups(id, limit, offset, status=null) {
        const params = offset != null && limit != null? 
            {limit, offset, status} : {status};
        const response = await AXIOS.execute(AXIOS.GET, ItemApi.uri + `/${id}/itemrequestgroups/list`,
            null, null, null, params)
        return response.data
    }
}

export class ItemRequestGroupApi {
    static uri = '/inventory/api/itemrequestgroups'

    static async listItemRequestGroups(limit, offset, search=null, status=null) {
        const params = offset != null && limit != null? 
            {limit, offset, search, status} : {search, status};
        const response = await AXIOS.execute(AXIOS.GET, ItemRequestGroupApi.uri + `/list`,
            null, null, null, params)
        return response.data
    }

    static async retrieveItemRequestGroup(id) {
        const response = await AXIOS.execute(AXIOS.GET, ItemRequestGroupApi.uri + `/${id}/`)
        return response.data
    }
}

export class ItemRequestApi {
    static uri = '/inventory/api/itemrequests'

    static async retrieveItemRequest(id) {
        const response = await AXIOS.execute(AXIOS.GET, ItemRequestApi.uri + `/${id}/`,
            null, null, null)
        return response.data
    }

    static async updateItemRequest(id, params) {
        const response = await AXIOS.execute(AXIOS.POST, ItemRequestApi.uri + `/${id}/update`,
            null, null, null, params)
        return response.data
    }
}

export class ItemPropertiesApi {
    static uri = '/inventory/api/items/properties'

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
