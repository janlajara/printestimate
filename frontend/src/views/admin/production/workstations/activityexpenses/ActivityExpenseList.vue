<template>
    <div>
        <Button icon="add" color="tertiary"
            @click="()=>state.createEditModal.open()">Add Expense</Button>
        <ActivityExpenseModal 
            :workstation-id="state.id"
            :activity-expense-id="state.createEditModal.data.id"
            :is-open="state.createEditModal.isOpen"
            @toggle="state.createEditModal.toggle" 
            :on-after-save="populateActivityExpenses"/>
        <Table :headers="['Name', 'Rate', '']" :loader="state.isProcessing">
            <Row v-for="(s, key) in state.list" :key="key" clickable>
                <Cell label="Name">{{s.name}}</Cell>
                <Cell label="Rate">{{s.rateFormatted}}</Cell>
                <Cell>
                    <div class="w-full flex justify-end">
                        <Button class="my-auto" icon="edit"
                            @click="()=>state.createEditModal.open(s.id)"/>
                        <Button class="my-auto" icon="delete"
                            @click="()=>state.deleteDialog.open(s.id, s.name)"/>
                    </div>
                </Cell>
            </Row>
        </Table>
        <DeleteRecordDialog 
            heading="Delete Expense"
            :is-open="state.deleteDialog.isOpen"
            :execute="state.deleteDialog.delete"
            :on-after-execute="populateActivityExpenses"
            @toggle="state.deleteDialog.toggle">
            <div>
                Are you sure you want to delete 
                <span class="font-bold">
                    {{state.deleteDialog.data.name}}</span>?
            </div>
        </DeleteRecordDialog>
    </div>
</template>

<script>
import Table from '@/components/Table.vue';
import Row from '@/components/Row.vue';
import Cell from '@/components/Cell.vue';
import Button from '@/components/Button.vue';
import DeleteRecordDialog from '@/components/DeleteRecordDialog.vue';
import ActivityExpenseModal from '@/views/admin/production/workstations/activityexpenses/ActivityExpenseModal.vue';

import {reactive, onBeforeMount} from 'vue';
import {WorkstationApi, ActivityExpenseApi} from '@/utils/apis.js';

export default {
    components: {
        Table, Row, Cell, Button, DeleteRecordDialog, ActivityExpenseModal
    },
    props: {
        workstationId: Number
    },
    setup(props) {
        const state = reactive({
            id: props.workstationId,
            isProcessing: false,
            list: [],
            createEditModal: {
                isOpen: false,
                data: {
                    id: null
                },
                toggle: value => state.createEditModal.isOpen = value,
                open: (id) => {
                    state.createEditModal.data.id = id;
                    state.createEditModal.toggle(true);
                }
            },
            deleteDialog: {
                isOpen: false,
                data: {
                    id: null, name: null
                },
                toggle: value => state.deleteDialog.isOpen = value,
                open: (id, name) => {
                    state.deleteDialog.data = {id, name};
                    state.deleteDialog.toggle(true);
                },
                delete: async () => {
                    await deleteActivityExpense(state.deleteDialog.data.id);
                }
            }
        })

        const populateActivityExpenses = async ()=> {
            state.isProcessing = true;
            if (state.id) {
                const response = await WorkstationApi.retrieveWorkstationActivityExpenses(state.id);
                if (response) {
                    state.list = response.map(obj=> ({
                        id: obj.id,
                        name: obj.name,
                        type: obj.type,
                        rate: obj.rate,
                        rateFormatted: obj.rate_formatted
                    }));
                }
            }
            state.isProcessing = false;
        }

        const deleteActivityExpense = async (id) => {
            state.isProcessing = true;
            if (id)  ActivityExpenseApi.deleteActivityExpense(id);
            state.isProcessing = false;
        }

        onBeforeMount(populateActivityExpenses);

        return {
            state, populateActivityExpenses, deleteActivityExpense
        }
    }
}
</script>