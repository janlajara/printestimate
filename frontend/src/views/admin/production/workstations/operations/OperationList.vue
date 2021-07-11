<template>
    <div>
        <Button icon="add" color="tertiary" :disabled="state.isProcessing"
            @click="()=>state.createEditModal.open()">Add Operation</Button>
        <OperationModal 
            :workstation-id="state.id"
            :operation-id="state.createEditModal.data.id"
            :is-open="state.createEditModal.isOpen"
            @toggle="state.createEditModal.toggle" 
            :on-after-save="populateOperations"/>
        <Table :headers="['Name', '']" :loader="state.isProcessing">
            <Row v-for="(s, key) in state.list" :key="key" clickable>
                <Cell label="Name">{{s.name}}</Cell>
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
            heading="Delete Operation"
            :is-open="state.deleteDialog.isOpen"
            :execute="state.deleteDialog.delete"
            :on-after-execute="populateOperations"
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
import OperationModal from '@/views/admin/production/workstations/operations/OperationModal.vue';

import {reactive, onBeforeMount} from 'vue';
import {WorkstationApi, OperationApi} from '@/utils/apis.js';

export default {
    components: {
        Table, Row, Cell, Button, DeleteRecordDialog, OperationModal
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
                    deleteOperation(state.deleteDialog.data.id);
                }
            }
        });

        const populateOperations = async ()=> {
            state.isProcessing = true;
            if (state.id) {
                const response = await WorkstationApi.retrieveWorkstationOperations(state.id);
                if (response) {
                    state.list = response.map(obj=> ({
                        id: obj.id,
                        name: obj.name
                    }));
                }
            }
            state.isProcessing = false;
        }

        const deleteOperation = async (id) => {
            state.isProcessing = true;
            if (id)  await OperationApi.deleteOperation(id);
            state.isProcessing = false;
        }

        onBeforeMount(populateOperations);

        return {
            state, populateOperations, deleteOperation
        }
    }
}
</script>