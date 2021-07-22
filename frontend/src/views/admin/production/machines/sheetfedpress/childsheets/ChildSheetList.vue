<template>
    <div>
        <Button icon="add" color="tertiary"
            @click="()=>state.createEditModal.open()">Add Child Sheet</Button>
        <ChildSheetModal 
            :machine-id="state.id"
            :child-sheet-id="state.createEditModal.data.id"
            :is-open="state.createEditModal.isOpen"
            @toggle="state.createEditModal.toggle" 
            :on-after-save="()=>populateChildSheets(state.id)"/>
        <Table layout="fixed" :loader="state.isProcessing"
            :cols-width="['w-1/6', 'w-1/4', 'w-1/4', 'w-1/4']"
            :headers="['Lay-out', 'Size', 'Parent Sheet', '']">
            <Row v-for="(s, key) in state.list" :key="key" clickable>
                <Cell label="Lay-out" class="bg-gray-100">
                    <Svg :svg-height="50" 
                        :view-box-width="s.widthValue" 
                        :view-box-height="s.lengthValue"
                        class="bg-gray">
                        <ChildSheetShape 
                            :width="s.widthValue"
                            :length="s.lengthValue"
                            :margin-top="s.marginTop"
                            :margin-right="s.marginRight"
                            :margin-bottom="s.marginBottom"
                            :margin-left="s.marginLeft"
                            :view-box-width="s.widthValue"
                            :view-box-length="s.lengthValue"/>
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
                <Cell label="Parent Sheet">
                    {{s.parent}}
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
            heading="Delete Sheet"
            :is-open="state.deleteDialog.isOpen"
            :execute="state.deleteDialog.delete"
            :on-after-execute="()=>populateChildSheets(state.id)"
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
import ChildSheetModal from '@/views/admin/production/machines/sheetfedpress/childsheets/ChildSheetModal.vue';
import ChildSheetShape from '@/views/admin/production/machines/sheetfedpress/childsheets/ChildSheetShape.vue';
import Svg from '@/utils/svg/Svg.vue';

import {reactive, onBeforeMount} from 'vue';
import {SheetFedPressMachineApi, ChildSheetApi} from '@/utils/apis.js';

export default {
    components: {
        Table, Row, Cell, Button, DeleteRecordDialog, 
        ChildSheetModal, ChildSheetShape, Svg
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
                    await deleteChildSheet(state.deleteDialog.data.id);
                }
            }
        })

        const populateChildSheets = async (id)=> {
            state.isProcessing = true;
            if (id) {
                const response = await SheetFedPressMachineApi.retrieveSheetFedPressMachineChildSheets(id);
                if (response) {
                    state.list = response.map(obj=> ({
                        id: obj.id,
                        parent: obj.parent_size,
                        size: obj.size,
                        label: obj.label,
                        widthValue: obj.width_value,
                        lengthValue: obj.length_value,
                        sizeUom: obj.size_uom,
                        marginTop: obj.margin_top,
                        marginRight: obj.margin_right,
                        marginBottom: obj.margin_bottom,
                        marginLeft: obj.margin_left
                    }));
                }
            }
            state.isProcessing = false;
        }

        const deleteChildSheet = async (id) => {
            state.isProcessing = true;
            if (id)  await ChildSheetApi.deleteChildSheet(id);
            state.isProcessing = false;
        }

        onBeforeMount(()=>{
            populateChildSheets(state.id)
        });

        return {
            state, populateChildSheets, deleteChildSheet
        }
    }
}
</script>