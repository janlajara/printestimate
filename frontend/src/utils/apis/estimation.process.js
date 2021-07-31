import {AXIOS} from '@/utils/apis/core.js'


export class WorkstationApi {
    static uri = '/estimation/api/workstations'

    static async listWorkstations() {
        const response = await AXIOS.execute(AXIOS.GET, WorkstationApi.uri);
        if (response) return response.data;
    }

    static async createWorkstation(workstation) {
        const response = await AXIOS.execute(AXIOS.POST, WorkstationApi.uri, 
            'Workstation created successfully.', 'Create failed. Please try again.', workstation);
        return response;
    }

    static async retrieveWorkstation(id) {
        const response = await AXIOS.execute(AXIOS.GET, WorkstationApi.uri + `/${id}`)
        return response.data
    }

    static async retrieveWorkstationActivityExpenses(id, getOptions=false) {
        const action = (getOptions)? AXIOS.OPTIONS : AXIOS.GET;
        const response = await AXIOS.execute(action, WorkstationApi.uri + `/${id}/activityexpenses`)
        return response.data
    }

    static async createWorkstationActivityExpense(id, activityExpense) {
        const response = await AXIOS.execute(AXIOS.POST, WorkstationApi.uri + `/${id}/activityexpenses`,
            'Expense created successfully.', 'Create failed. Please try again.', activityExpense);
        return response.data;
    }

    static async retrieveWorkstationActivities(id, getOptions=false) {
        const action = (getOptions)? AXIOS.OPTIONS : AXIOS.GET;
        const response = await AXIOS.execute(action, WorkstationApi.uri + `/${id}/activities`)
        return response.data
    }

    static async createWorkstationActivity(id, activity) {
        const response = await AXIOS.execute(AXIOS.POST, WorkstationApi.uri + `/${id}/activities`,
            'Activity created successfully.', 'Create failed. Please try again.', activity);
        return response.data;
    }

    static async retrieveWorkstationOperations(id, getOptions=false) {
        const action = (getOptions)? AXIOS.OPTIONS : AXIOS.GET;
        const response = await AXIOS.execute(action, WorkstationApi.uri + `/${id}/operations`)
        return response.data
    }

    static async createWorkstationOperation(id, operation) {
        const response = await AXIOS.execute(AXIOS.POST, WorkstationApi.uri + `/${id}/operations`,
            'Operation created successfully.', 'Create failed. Please try again.', operation);
        return response.data;
    }

    static async updateWorkstation(id, workstation) {
        const response = await AXIOS.execute(AXIOS.PUT, WorkstationApi.uri + `/${id}/`, 
            'Workstation updated successfully.', 'Update failed. Please try again.', workstation
        )
        if (response) return response.data;
    }

    static async deleteWorkstation(id) {
        await AXIOS.execute(AXIOS.DELETE, WorkstationApi.uri + `/${id}/`, 
            'Workstation deleted successfully.', 'Delete failed. Please try again.');
    }
}


export class ActivityExpenseApi {
    static uri = '/estimation/api/activityexpenses'

    static async retrieveActivityExpense(id) {
        const response = await AXIOS.execute(AXIOS.GET, ActivityExpenseApi.uri + `/${id}`)
        return response.data
    }

    static async updateActivityExpense(id, activityExpense) {
        const response = await AXIOS.execute(AXIOS.PUT, ActivityExpenseApi.uri + `/${id}/`, 
            'Activity expense updated successfully.', 'Update failed. Please try again.', activityExpense
        )
        if (response) return response.data;
    }

    static async deleteActivityExpense(id) {
        await AXIOS.execute(AXIOS.DELETE, ActivityExpenseApi.uri + `/${id}/`, 
            'Activity expense deleted successfully.', 'Delete failed. Please try again.');
    }
}

export class ActivityApi {
    static uri = '/estimation/api/activities'

    static async retrieveActivity(id) {
        const response = await AXIOS.execute(AXIOS.GET, ActivityApi.uri + `/${id}`)
        return response.data
    }

    static async updateActivity(id, activity) {
        const response = await AXIOS.execute(AXIOS.PUT, ActivityApi.uri + `/${id}/`, 
            'Activity updated successfully.', 'Update failed. Please try again.', activity
        )
        if (response) return response.data;
    }

    static async deleteActivity(id) {
        await AXIOS.execute(AXIOS.DELETE, ActivityApi.uri + `/${id}/`, 
            'Activity deleted successfully.', 'Delete failed. Please try again.');
    }
}

export class OperationApi {
    static uri = '/estimation/api/operations'

    static async listOperationCostingMeasures() {
        const response = await AXIOS.execute(AXIOS.GET, OperationApi.uri + `/costingmeasures`)
        return response.data
    }

    static async retrieveOperation(id) {
        const response = await AXIOS.execute(AXIOS.GET, OperationApi.uri + `/${id}`)
        return response.data
    }

    static async retrieveOperationSteps(id) {
        const response = await AXIOS.execute(AXIOS.GET, OperationApi.uri + `/${id}/steps`)
        return response.data
    }

    static async createOperationStep(id, operationStep) {
        const response = await AXIOS.execute(AXIOS.POST, OperationApi.uri + `/${id}/steps`,
            'Operation step created successfully.', 'Create failed. Please try again.', operationStep);
        return response.data;
    }

    static async updateOperation(id, operation) {
        const response = await AXIOS.execute(AXIOS.PUT, OperationApi.uri + `/${id}/`, 
            'Operation updated successfully.', 'Update failed. Please try again.', operation
        )
        if (response) return response.data;
    }

    static async deleteOperation(id) {
        await AXIOS.execute(AXIOS.DELETE, OperationApi.uri + `/${id}/`, 
            'Operation deleted successfully.', 'Delete failed. Please try again.');
    }
}


export class OperationStepApi {
    static uri = '/estimation/api/operationsteps'

    static async retrieveOperationStep(id) {
        const response = await AXIOS.execute(AXIOS.GET, OperationStepApi.uri + `/${id}`)
        return response.data
    }

    static async updateOperationStep(id, operationStep) {
        const response = await AXIOS.execute(AXIOS.PUT, OperationStepApi.uri + `/${id}/`, 
            'Operation step updated successfully.', 'Update failed. Please try again.', operationStep)
        if (response) return response.data;
    }

    static async deleteOperationStep(id) {
        await AXIOS.execute(AXIOS.DELETE, OperationStepApi.uri + `/${id}/`, 
            'Operation step deleted successfully.', 'Delete failed. Please try again.');
    }
}