<template>
    <div>
        <Button color="secondary" icon="add"
            :action="()=>state.modal.open()">
            Create</Button>
        <TemplateCostAddonModal 
            :template-cost-addon-id="state.modal.templateCostAddonId"
            :is-open="state.modal.isOpen"
            @toggle="value => state.modal.toggle(value)"
            @saved="listTemplateCostAddons"/>
        <div class="grid md:grid-cols-3">
            <Table :headers="['Name', 'Add-ons', '', '']" :loader="state.isProcessing"
                class="col-span-2">
                <Row v-for="(s, key) in state.list" :key="key">
                    <Cell label="Name" >
                        <span>{{s.name}}</span>
                    </Cell>
                    <Cell label="Add-ons">
                        <ul class="list-disc">
                            <li v-for="(addon, key) in s.templateCostAddonItems" :key="key">
                                <span>{{addon.configCostAddon.name}}</span>
                            </li>
                        </ul>
                        <span v-if="s.allowCustomValue"
                            class="-ml-3 mt-4 text-xs italic text-secondary-dark">
                            *Custom value allowed.</span>
                    </Cell>
                    <Cell>
                        <span v-if="s.isDefault" class="inline-flex items-center px-2.5 py-0.5 
                            rounded-full text-xs font-medium bg-secondary"> Default </span>
                    </Cell>
                    <Cell>
                        <div class="flex justify-end">
                            <Button class="my-auto" icon="edit" 
                                @click="()=> state.modal.open(s.id)"/>
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
                :on-after-execute="listTemplateCostAddons"
                @toggle="state.deleteDialog.toggle">
                <div>
                    Are you sure you want to delete 
                    <span class="font-bold">
                        {{state.deleteDialog.data.name}}</span>?
                </div>
            </DeleteRecordDialog>
        </div>
    </div> 
</template>
<script>
import Button from '@/components/Button.vue';
import Table from '@/components/Table.vue';
import Row from '@/components/Row.vue';
import Cell from '@/components/Cell.vue';
import DeleteRecordDialog from '@/components/DeleteRecordDialog.vue';
import TemplateCostAddonModal from './TemplateCostAddonModal.vue';

import {reactive, onBeforeMount} from 'vue';
import {CostAddonApi} from '@/utils/apis.js';

export default {
    components: {
        Button, Table, Row, Cell, TemplateCostAddonModal, DeleteRecordDialog
    },
    setup() {
        const state = reactive({
            isProcessing: false,
            list: [],
            modal: {
                isOpen: false,
                templateCostAddonId: null,
                toggle: (value)=> {
                    state.modal.isOpen = value;
                },
                open: (id=null)=> {
                    state.modal.templateCostAddonId = id;
                    state.modal.toggle(true);
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
                    await deleteTemplateCostAddon(state.deleteDialog.data.id);
                }
            }
        });

        const deleteTemplateCostAddon = async (id) => {
            if (id) await CostAddonApi.deleteTemplateCostAddon(id);
        }

        const listTemplateCostAddons = async ()=> {
            state.isProcessing = true;
            const response = await CostAddonApi.listTemplateCostAddons();
            if (response) {
                state.list = response.map(x => ({
                    id: x.id, name: x.name,
                    isDefault: x.is_default,
                    templateCostAddonItems: x.template_cost_addon_items.map(y => ({
                        id: y.id, sequence: y.sequence,
                        configCostAddon: {
                            id: y.config_cost_addon.id,
                            name: y.config_cost_addon.name
                        }
                    }))
                }));
            }
            state.isProcessing = false;
        };

        onBeforeMount(()=> {
            listTemplateCostAddons();
        });

        return {
            state, listTemplateCostAddons
        }
    },
}
</script>
