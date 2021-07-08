<template>
    <div>
        <Button icon="add" color="tertiary" :disabled="state.isProcessing"
            @click="()=>state.createEditModal.open()">Add Activity</Button>
        <ActivityModal 
            :workstation-id="state.id"
            :activity-id="state.createEditModal.data.id"
            :is-open="state.createEditModal.isOpen"
            @toggle="state.createEditModal.toggle" 
            :on-after-save="populateActivities"/>
        <Table :headers="['Name', 'Speed', 'Hourly Rate', 'Measure Rate', 'Flat Rate', '']" :loader="state.isProcessing">
            <Row v-for="(s, key) in state.list" :key="key" clickable>
                <Cell label="Name">{{s.name}}</Cell>
                <Cell label="Speed">{{s.speed.rate}}</Cell>
                <Cell label="Hourly Rate">{{s.hourlyRate}}</Cell>
                <Cell label="Measure Rate">{{s.measureRate}}</Cell>
                <Cell label="Flat Rate">{{s.flatRate}}</Cell>
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
            heading="Delete Activity"
            :is-open="state.deleteDialog.isOpen"
            :execute="state.deleteDialog.delete"
            :on-after-execute="populateActivities"
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
import ActivityModal from '@/views/admin/production/workstations/activities/ActivityModal.vue';

import {reactive, onBeforeMount} from 'vue';
import {WorkstationApi, ActivityApi} from '@/utils/apis.js';

export default {
    components: {
        Table, Row, Cell, Button, DeleteRecordDialog, ActivityModal
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
                delete: () => {
                    deleteActivity(state.deleteDialog.data.id);
                }
            }
        });

        const populateActivities = async ()=> {
            state.isProcessing = true;
            if (state.id) {
                const response = await WorkstationApi.retrieveWorkstationActivities(state.id);
                if (response) {
                    state.list = response.map(obj=> ({
                        id: obj.id,
                        name: obj.name,
                        speed: {
                            id: obj.speed.id,
                            rate: obj.speed.rate
                        },
                        measureUnit: obj.ream,
                        flatRate: obj.flat_rate_formatted,
                        measureRate: obj.measure_rate_formatted,
                        hourlyRate: obj.hourly_rate_formatted
                    }));
                }
            }
            state.isProcessing = false;
        }

        const deleteActivity = async (id) => {
            state.isProcessing = true;
            if (id)  ActivityApi.deleteActivity(id);
            state.isProcessing = false;
        }

        onBeforeMount(populateActivities);

        return {
            state, populateActivities, deleteActivity
        }
    }
}
</script>