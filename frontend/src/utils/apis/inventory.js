import {showToast, reference, AXIOS} from '@/utils/apis/core.js'


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

    static async listItems(limit, offset, search, filter=null) {
        const params = offset != null && limit != null? 
            {limit, offset, search, ...filter} : {search, ...filter};
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

    static async listItemStocks(id, limit, offset, availableOnly=false, search=null) {
        const params = offset != null && limit != null? 
            {limit, offset, "available-only": availableOnly, search} : {search};
        const response = await AXIOS.execute(AXIOS.GET, ItemApi.uri + `/${id}/stocks/list`,
            null, null, null, params)
        return response.data
    }

    static async depositStock(id, stock) {
        const response = await AXIOS.execute(AXIOS.POST, ItemApi.uri + `/${id}/stocks/deposit`,
            'Stock deposited successfully.', 'Deposit failed. Please try again.', stock);
        return response.data
    }

    static async requestStocks(id, requests) {
        const response = await AXIOS.execute(AXIOS.POST, ItemApi.uri + `/${id}/stocks/request`,
            null, 'Stock request failed. Please try again.', requests);
        if (response.data) {
            const requestId = reference.formatId(response.data.id, reference.mrs)
            showToast("success", `Request ${requestId} has been saved.`);
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
        const response = await AXIOS.execute(AXIOS.GET, ItemRequestGroupApi.uri,
            null, null, null, params)
        return response.data
    }

    static async createItemRequestGroup(request) {
        const response = await AXIOS.execute(AXIOS.POST, ItemRequestGroupApi.uri,
            'MRS created', 'Failed to created MRS. Please try again.', request)
        return response.data    
    }

    static async retrieveItemRequestGroup(id) {
        const response = await AXIOS.execute(AXIOS.GET, ItemRequestGroupApi.uri + `/${id}/`)
        return response.data
    }

    static async updateItemRequestGroup(id, request) {
        const response = await AXIOS.execute(AXIOS.PUT, ItemRequestGroupApi.uri + `/${id}/`,
            'MRS updated', 'Failed to update MRS. Please try again.', request)
        return response.data
    }

    static async deleteItemRequestGroup(id) {
        const response = await AXIOS.execute(AXIOS.DELETE, ItemRequestGroupApi.uri + `/${id}/`,
            'MRS deleted', 'Failed to delete MRS. Please try again.')
        return response.data
    }

    static async addItemRequest(id, request) {
        const response = await AXIOS.execute(AXIOS.PUT, ItemRequestGroupApi.uri + `/${id}/itemrequest/add`,
            'Item request added', 'Failed to add item request. Please try again.', request)
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

    static async updateItemRequest(id, request) {
        const response = await AXIOS.execute(AXIOS.PUT, ItemRequestApi.uri + `/${id}/`,
            'Item Request updated', 'Update failed. Please try again.', request)
        return response.data
    }

    static async deleteItemRequest(id) {
        await AXIOS.execute(AXIOS.DELETE, ItemRequestApi.uri + `/${id}/`,
            null, null, null)
    }

    static async updateItemRequestStatus(id, request) {
        const response = await AXIOS.execute(AXIOS.PUT, ItemRequestApi.uri + `/${id}/status/update`,
            'Status changed', 'Action failed. Please try again.', request)
        return response.data
    }
}

export class StockRequestApi {
    static uri = '/inventory/api/stockrequests'

    static async deleteStockRequest(id) {
        await AXIOS.execute(AXIOS.DELETE, StockRequestApi.uri + `/${id}/`,
            null, null, null);
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