import {AXIOS} from '@/utils/apis/core.js'

export class CostAddonApi {
    static uri = '/estimation/api/costaddons';
    static config_uri = CostAddonApi.uri + '/config';
    static template_uri = CostAddonApi.uri + '/template';

    static async listConfigCostAddons(getOptions=false) {
        const action = getOptions? AXIOS.OPTIONS : AXIOS.GET;
        const response = await AXIOS.execute(action, 
            CostAddonApi.config_uri);
        if (response) return response.data;
    }

    static async createConfigCostAddon(configCostAddon) {
        const response = await AXIOS.execute(AXIOS.POST, 
            CostAddonApi.config_uri, 'Config Cost Add-on created successfully.', 
            'Create failed. Please try again.', configCostAddon);
        return response;
    }

    static async retrieveConfigCostAddon(id) {
        const response = await AXIOS.execute(AXIOS.GET, 
            CostAddonApi.config_uri + `/${id}/`)
        return response.data
    }

    static async updateConfigCostAddon(id, configCostAddon) {
        const response = await AXIOS.execute(AXIOS.PUT, 
            CostAddonApi.config_uri + `/${id}/`, 'Config Cost Add-on updated successfully.', 
            'Update failed. Please try again.', configCostAddon)
        if (response) return response.data;
    }

    static async deleteConfigCostAddon(id) {
        await AXIOS.execute(AXIOS.DELETE, CostAddonApi.config_uri + `/${id}/`, 
            'Config Cost Add-on deleted successfully.', 'Delete failed. Please try again.');
    }

    static async listTemplateCostAddons(getOptions=false) {
        const action = getOptions? AXIOS.OPTIONS : AXIOS.GET;
        const response = await AXIOS.execute(action, 
            CostAddonApi.template_uri);
        if (response) return response.data;
    }

    static async createTemplateCostAddon(templateCostAddon) {
        const response = await AXIOS.execute(AXIOS.POST, 
            CostAddonApi.template_uri, 'Template Cost Add-on created successfully.', 
            'Create failed. Please try again.', templateCostAddon);
        return response;
    }

    static async retrieveTemplateCostAddon(id) {
        const response = await AXIOS.execute(AXIOS.GET, 
            CostAddonApi.template_uri + `/${id}/`)
        return response.data
    }

    static async updateTemplateCostAddon(id, templateCostAddon) {
        const response = await AXIOS.execute(AXIOS.PUT, 
            CostAddonApi.template_uri + `/${id}/`, 'Template Cost Add-on updated successfully.', 
            'Update failed. Please try again.', templateCostAddon)
        if (response) return response.data;
    }

    static async deleteTemplateCostAddon(id) {
        await AXIOS.execute(AXIOS.DELETE, CostAddonApi.template_uri + `/${id}/`, 
            'Template Cost Add-on deleted successfully.', 'Delete failed. Please try again.');
    }

}