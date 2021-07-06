<template>
    <div>
        <Button icon="add" color="tertiary"
            @click="()=>state.createEditModal.open()">Add Expense</Button>
        <ActivityExpenseModal 
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
    </div>
</template>

<script>
import Table from '@/components/Table.vue';
import Row from '@/components/Row.vue';
import Cell from '@/components/Cell.vue';
import Button from '@/components/Button.vue';
import ActivityExpenseModal from '@/views/admin/production/workstations/activityexpenses/ActivityExpenseModal.vue';

import {reactive, onBeforeMount} from 'vue';
import {WorkstationApi} from '@/utils/apis.js';

export default {
    components: {
        Table, Row, Cell, Button, ActivityExpenseModal
    },
    props: {
        workstationId: String
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
                delete: () => {}
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

        onBeforeMount(populateActivityExpenses);

        return {
            state, populateActivityExpenses
        }
    }
}
</script>