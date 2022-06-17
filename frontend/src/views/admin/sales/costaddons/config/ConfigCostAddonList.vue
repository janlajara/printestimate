<template>
    <div>
        <Button color="secondary" icon="add"
            :action="()=>state.modal.open()">
            Create</Button>
        <ConfigCostAddonModal 
            :config-cost-addon-id="state.modal.configCostAddonId"
            :is-open="state.modal.isOpen"
            @toggle="value => state.modal.toggle(value)"
            @saved="listConfigCostAddons"/>
        <div class="grid md:grid-cols-3">
            <Table :headers="['Name', 'Options', '']" :loader="state.isProcessing"
                class="col-span-2">
                <Row v-for="(s, key) in state.list" :key="key">
                    <Cell label="Name">{{s.name}}</Cell>
                    <Cell label="Options">
                        <div class="pl-6">
                            <ul class="list-disc">
                                <li v-for="(option, key) in s.options" :key="key">
                                    <div class="grid grid-cols-2">
                                        <span>{{option.label}}</span>
                                        <span>{{option.formattedValue}}</span>
                                    </div>
                                </li>
                            </ul>
                            <div v-if="s.allowCustomValue || s.isRequired"
                                class="-ml-3 mt-4 text-xs italic text-secondary-dark">
                                *<span v-if="s.isRequired">Required. </span>
                                <span v-if="s.allowCustomValue">Custom value allowed.</span>
                            </div>
                        </div>
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
                :on-after-execute="listConfigCostAddons"
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
import ConfigCostAddonModal from './ConfigCostAddonModal.vue';

import {reactive, onBeforeMount} from 'vue';
import {CostAddonApi} from '@/utils/apis.js';

export default {
    components: {
        Button, Table, Row, Cell, ConfigCostAddonModal, DeleteRecordDialog
    },
    setup() {
        const state = reactive({
            isProcessing: false,
            list: [],
            modal: {
                isOpen: false,
                configCostAddonId: null,
                toggle: (value)=> {
                    state.modal.isOpen = value;
                },
                open: (id=null)=> {
                    state.modal.configCostAddonId = id;
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
                    await deleteConfigCostdAddon(state.deleteDialog.data.id);
                }
            }
        });

        const deleteConfigCostdAddon = async (id) => {
            if (id) await CostAddonApi.deleteConfigCostAddon(id);
        }

        const listConfigCostAddons = async ()=> {
            state.isProcessing = true;
            const response = await CostAddonApi.listConfigCostAddons();
            if (response) {
                state.list = response.map(x => ({
                    id: x.id, name: x.name,
                    allowCustomValue: x.allow_custom_value,
                    isRequired: x.is_required,
                    options: x.config_cost_addon_options.map(y => ({
                        id: y.id, label: y.label,
                        formattedValue: y.formatted_value,
                    }))
                }));
            }
            state.isProcessing = false;
        };

        onBeforeMount(()=> {
            listConfigCostAddons();
        });

        return {
            state, listConfigCostAddons
        }
    },
}
</script>
