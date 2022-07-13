import {AXIOS} from '@/utils/apis/core.js'

export class ItemsWorkbookApi {
    static uri = '/fileio/api/inventory/items';

    static async downloadItemsWorkbook(filename) {
        const response = await AXIOS.download(
            ItemsWorkbookApi.uri,
            "Download successful!",
            "Failed to download the excel file.",
            filename);
        if (response) return response.status;
    }
}


export class CostEstimateWorkbookApi {
    static uri = '/fileio/api/estimation/costestimates';

    static async downloadCostEstimateWorkbook(id, filename) {
        const response = await AXIOS.download(
            `${CostEstimateWorkbookApi.uri}/${id}/`,
            "Download successful!",
            "Failed to download the excel file.",
            filename);
        if (response) return response.status;
    }
}