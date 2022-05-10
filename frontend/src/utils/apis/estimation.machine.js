import {AXIOS} from '@/utils/apis/core.js'

export class MachineApi {
    static uri = '/estimation/api/machines'

    static async listMachines(filter) {
        const response = await AXIOS.execute(AXIOS.GET, MachineApi.uri, null, null,
            null, filter);
        if (response) return response.data;
    }

    static async listMachineTypes() {
        const response = await AXIOS.execute(AXIOS.GET, MachineApi.uri + '/types');
        if (response) return response.data;
    }
}


export class SheetFedPressMachineApi {
    static uri = '/estimation/api/machines/sheetfedpress'

    static async listSheetFedPressMachines(getOptions=false) {
        const action = (getOptions)? AXIOS.OPTIONS : AXIOS.GET;
        const response = await AXIOS.execute(action, 
            SheetFedPressMachineApi.uri);
        if (response) return response.data;
    }

    static async createSheetFedPressMachine(machine) {
        const response = await AXIOS.execute(AXIOS.POST, 
            SheetFedPressMachineApi.uri, 
            'Machine created successfully.', 'Create failed. Please try again.', machine);
        return response;
    }

    static async retrieveSheetFedPressMachine(id) {
        const response = await AXIOS.execute(AXIOS.GET, 
            SheetFedPressMachineApi.uri + `/${id}`)
        return response.data
    }

    static async updateSheetFedPressMachine(id, machine) {
        const response = await AXIOS.execute(AXIOS.PUT, 
            SheetFedPressMachineApi.uri + `/${id}/`, 
            'Machine updated successfully.', 'Update failed. Please try again.', machine
        )
        if (response) return response.data;
    }

    static async deleteSheetFedPressMachine(id) {
        await AXIOS.execute(AXIOS.DELETE, SheetFedPressMachineApi.uri + `/${id}/`, 
            'Machine deleted successfully.', 'Delete failed. Please try again.');
    }

    static async getSheetLayout(id, input) {
        const response = await AXIOS.execute(AXIOS.POST, 
            SheetFedPressMachineApi.uri + `/${id}/getlayout`,
            null, null, input);
        return response.data;
    }
}


export class RollFedPressMachineApi {
    static uri = '/estimation/api/machines/rollfedpress'

    static async listRollFedPressMachines(getOptions=false) {
        const action = (getOptions)? AXIOS.OPTIONS : AXIOS.GET;
        const response = await AXIOS.execute(action, 
            RollFedPressMachineApi.uri);
        if (response) return response.data;
    }

    static async createRollFedPressMachine(machine) {
        const response = await AXIOS.execute(AXIOS.POST, 
            RollFedPressMachineApi.uri, 
            'Machine created successfully.', 'Create failed. Please try again.', machine);
        return response;
    }

    static async retrieveRollFedPressMachine(id) {
        const response = await AXIOS.execute(AXIOS.GET, 
            RollFedPressMachineApi.uri + `/${id}`)
        return response.data
    }

    static async updateRollFedPressMachine(id, machine) {
        const response = await AXIOS.execute(AXIOS.PUT, 
            RollFedPressMachineApi.uri + `/${id}/`, 
            'Machine updated successfully.', 'Update failed. Please try again.', machine
        )
        if (response) return response.data;
    }

    static async deleteRollFedPressMachine(id) {
        await AXIOS.execute(AXIOS.DELETE, RollFedPressMachineApi.uri + `/${id}/`, 
            'Machine deleted successfully.', 'Delete failed. Please try again.');
    }

    static async getSheetLayout(id, input) {
        const response = await AXIOS.execute(AXIOS.POST, 
            RollFedPressMachineApi.uri + `/${id}/getlayout`,
            null, null, input);
        return response.data;
    }
}


export class ChildSheetApi {
    static uri = '/estimation/api/childsheets'

    static async getSheetLayout(input) {
        const response = await AXIOS.execute(AXIOS.POST, 
            ChildSheetApi.uri + `/getlayout`, null, null, input);
        return response.data;
    }
}