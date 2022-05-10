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

    /* Not used anymore. To be removed
    static async retrieveSheetFedPressMachineParentSheets(id) {
        const response = await AXIOS.execute(AXIOS.GET, 
            SheetFedPressMachineApi.uri + `/sheetfedpress/${id}/parentsheets`)
        return response.data
    }

    static async createSheetFedPressMachineParentSheet(id, sheet) {
        const response = await AXIOS.execute(AXIOS.POST, 
            SheetFedPressMachineApi.uri + `/sheetfedpress/${id}/parentsheets`,
            'Parent Sheet created successfully.', 'Create failed. Please try again.', sheet);
        return response.data;
    }

    static async retrieveSheetFedPressMachineChildSheets(id) {
        const response = await AXIOS.execute(AXIOS.GET, 
            SheetFedPressMachineApi.uri + `/sheetfedpress/${id}/childsheets`)
        return response.data
    }

    static async createSheetFedPressMachineChildSheet(id, sheet) {
        const response = await AXIOS.execute(AXIOS.POST, 
            SheetFedPressMachineApi.uri + `/sheetfedpress/${id}/childsheets`,
            'Child Sheet created successfully.', 'Create failed. Please try again.', sheet);
        return response.data;
    }*/

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
/* Not used anymore. To be removed.
export class ParentSheetApi { 
    static uri = '/estimation/api/parentsheets'

    static async retrieveParentSheet(id) {
        const response = await AXIOS.execute(AXIOS.GET, ParentSheetApi.uri + `/${id}`)
        return response.data
    }

    static async updateParentSheet(id, sheet) {
        const response = await AXIOS.execute(AXIOS.PUT, ParentSheetApi.uri + `/${id}/`, 
            'Parent Sheet updated successfully.', 'Update failed. Please try again.', sheet
        )
        if (response) return response.data;
    }

    static async deleteParentSheet(id) {
        await AXIOS.execute(AXIOS.DELETE, ParentSheetApi.uri + `/${id}/`, 
            'Parent Sheet deleted successfully.', 'Delete failed. Please try again.');
    }
}


export class ChildSheetApi {
    static uri = '/estimation/api/childsheets'

    static async retrieveChildSheet(id) {
        const response = await AXIOS.execute(AXIOS.GET, ChildSheetApi.uri + `/${id}`)
        return response.data
    }

    static async updateChildSheet(id, sheet) {
        const response = await AXIOS.execute(AXIOS.PUT, ChildSheetApi.uri + `/${id}/`, 
            'Child Sheet updated successfully.', 'Update failed. Please try again.', sheet
        )
        if (response) return response.data;
    }

    static async deleteChildSheet(id) {
        await AXIOS.execute(AXIOS.DELETE, ChildSheetApi.uri + `/${id}/`, 
            'Child Sheet deleted successfully.', 'Delete failed. Please try again.');
    }

    static async retrieveChildSheetLayout(sheet) {
        const response = await AXIOS.execute(AXIOS.POST, 
            ChildSheetApi.uri + `/layout`,null, null, sheet);
        return response.data
    }

    static async getSheetLayout(input) {
        const response = await AXIOS.execute(AXIOS.POST, 
            ChildSheetApi.uri + `/getlayout`, null, null, input);
        return response.data;
    }
}
*/
