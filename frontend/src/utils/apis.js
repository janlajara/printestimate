const axios = require('axios')
const API_HOSTNAME = 'http://localhost:8000'

const AXIOS_POST = async (uri, obj)=> {
    const response = await axios.post(
        API_HOSTNAME + uri, obj
    );
    return response;
}

const AXIOS_GET = async (uri)=> {
    const response = await axios.get(
        API_HOSTNAME + uri
    );
    return response;
}

export class InventoryApi {
    static uri = '/inventory/api/item'

    static async createItem(item) {
        try {
            const response = await AXIOS_POST(InventoryApi.uri, item);
            console.log(response.data)
        } catch (err) {
            console.error(err);
        }
    }

    static async listItems() {
        const response = await AXIOS_GET(InventoryApi.item_uri);
        return response.data;
    }
}

export class BaseStockUnitApi {
    static uri = '/inventory/api/basestockunit'

    static async listBaseStockUnits() {
        const response = await AXIOS_GET(BaseStockUnitApi.uri);
        return response.data;
    }
}

export class AlternateStockUnitApi {
    static uri = '/inventory/api/alternatestockunit'

    static async listAlternateStockUnits() {
        const response = await AXIOS_GET(AlternateStockUnitApi.uri);
        return response.data;
    }
}
