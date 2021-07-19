<template>
    <div>
        <Button icon="add" color="tertiary"
            @click="()=>state.createEditModal.open()">Add Parent Sheet</Button>
        <ParentSheetModal 
            :machine-id="state.id"
            :parent-sheet-id="state.createEditModal.data.id"
            :is-open="state.createEditModal.isOpen"
            @toggle="state.createEditModal.toggle" 
            :on-after-save="()=>populateParentSheets(state.id)"/>
        <Table layout="fixed" :loader="state.isProcessing"
            :cols-width="['w-1/6', 'w-1/2', 'w-1/4']"
            :headers="['Lay-out', 'Size', '']">
            <Row v-for="(s, key) in state.list" :key="key" clickable>
                <Cell label="Lay-out" class="bg-gray-100">
                    <Svg :svg-height="50" 
                        :view-box-width="s.widthValue" 
                        :view-box-height="s.lengthValue"
                        class="bg-gray">
                        <ParentSheetShape
                            :width="s.widthValue"
                            :length="s.lengthValue"
                            :padding-top="s.paddingTop"
                            :padding-right="s.paddingRight"
                            :padding-bottom="s.paddingBottom"
                            :padding-left="s.paddingLeft"/>
                    </Svg>
                    <div class="text-xs flex justify-center">
                        {{s.size}}</div>
                </Cell>
                <Cell label="Size">
                    <span v-if="s.label">
                        {{s.label}} ({{s.size}})
                    </span>
                    <span v-else>
                        {{s.size}}
                    </span>
                </Cell>
                <Cell>
                    <div class="w-full flex justify-end">
                        <Button class="my-auto" icon="edit"
                            @click="()=>state.createEditModal.open(s.id)"/>
                        <Button class="my-auto" icon="delete"
                            @click="()=>state.deleteDialog.open(s.id, s.size)"/>
                    </div>
                </Cell>
            </Row>
        </Table>
        <DeleteRecordDialog 
            heading="Delete Expense"
            :is-open="state.deleteDialog.isOpen"
            :execute="state.deleteDialog.delete"
            :on-after-execute="()=>populateParentSheets(state.id)"
            @toggle="state.deleteDialog.toggle">
            <div>
                Are you sure you want to delete sheet
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
import ParentSheetModal from '@/views/admin/production/machines/sheetfedpress/parentsheets/ParentSheetModal.vue';
import Svg from '@/utils/svg/Svg.vue';
import ParentSheetShape from '@/views/admin/production/machines/sheetfedpress/parentsheets/ParentSheetShape.vue';

import {reactive, onBeforeMount} from 'vue';
import {SheetFedPressMachineApi, ParentSheetApi} from '@/utils/apis.js';

export default {
    components: {
        Table, Row, Cell, Button, DeleteRecordDialog, 
        ParentSheetModal, Svg, ParentSheetShape
    },
    props: {
        machineId: String
    },
    setup(props) {
        const state = reactive({
            id: props.machineId,
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
                    await deleteParentSheet(state.deleteDialog.data.id);
                }
            }
        })

        const populateParentSheets = async (id)=> {
            state.isProcessing = true;
            if (id) {
                const response = await SheetFedPressMachineApi.retrieveSheetFedPressMachineParentSheets(id);
                if (response) {
                    state.list = response.map(obj=> ({
                        id: obj.id,
                        size: obj.size,
                        label: obj.label,
                        widthValue: obj.width_value,
                        lengthValue: obj.length_value,
                        sizeUom: obj.size_uom,
                        paddingTop: obj.padding_top,
                        paddingRight: obj.padding_right,
                        paddingBottom: obj.padding_bottom,
                        paddingLeft: obj.padding_left
                    }));
                }
            }
            state.isProcessing = false;
        }

        const deleteParentSheet = async (id) => {
            state.isProcessing = true;
            if (id)  await ParentSheetApi.deleteParentSheet(id);
            state.isProcessing = false;
        }

        onBeforeMount(()=>{
            populateParentSheets(state.id)
        });

        return {
            state, populateParentSheets, deleteParentSheet
        }
    }
}
</script>