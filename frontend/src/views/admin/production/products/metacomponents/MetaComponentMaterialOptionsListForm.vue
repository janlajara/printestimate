<template>
    <div>
        <Table :headers="['Name', '']"
            layout="fixed" :cols-width="['w-2/3', 'w-1/3']">
            <Row v-for="(x, i) in state.materialList" :key="i">
                <Cell>{{x.label}}</Cell>
                <Cell class="lg:px-0">
                    <div class="flex justify-end">
                        <Button class="my-auto px-0" icon="clear" 
                            @click="()=>{state.removeMaterial(i)}"/>
                    </div>
                </Cell>
            </Row>
        </Table>
        <hr/>
        <div class="grid gap-4 md:grid-cols-3">
            <InputTextLookup name="Item" 
                placeholder="Search Items" class="flex-grow md:col-span-2"
                :value="state.materialForm.lookupText"
                @select="selected => state.materialForm.item = selected"
                @input="value => {
                    state.materialForm.lookupText = value;
                    listMaterials(value);
                }"
                :options="state.meta.materialChoices.map( option => ({
                    value: option.value,
                    title: option.label,
                    subtitle: option.type,
                    figure: option.figure
                }))"/>
            <div class="relative">
                <span class="flex justify-end md:absolute md:bottom-0 md:left-0">
                    <Button icon="add" class="my-auto border-gray-300 border"
                            @click="state.addMaterial">Add</Button>
                </span>
            </div>
        </div>
    </div>
</template>
<script>
import Table from '@/components/Table.vue';
import Row from '@/components/Row.vue';
import Cell from '@/components/Cell.vue';
import Button from '@/components/Button.vue';
import InputTextLookup from '@/components/InputTextLookup.vue';

import {reactive, computed, watch} from 'vue';
import {ItemApi} from '@/utils/apis.js';

export default {
    components: {
        Table, Row, Cell, Button, InputTextLookup
    },
    props: {
        materialType: String,
        value: Array
    },
    emits: ['input'],
    setup(props, {emit}) {
        const state = reactive({
            materialType: computed(()=> props.materialType),
            materialList: [],
            materialForm: {
                id: null,
                item: null,
                lookupText: '',
            },
            meta: {
                materialChoices: [],
            },
            clearMaterialForm: ()=> {
                state.materialForm = {
                    id: null,
                    item: null,
                    lookupText: null,
                }
            },
            addMaterial: ()=> {
                const material = state.meta.materialChoices.find(x => 
                    x.value == state.materialForm.item);
                const materialOption = {
                    id: state.materialForm.id,
                    item: state.materialForm.item,
                    label: material.label
                };
                state.materialList.push(materialOption);
                emit('input', state.materialList);
                state.clearMaterialForm();
            },
            removeMaterial: (index)=> {
                state.materialList.splice(index, 1)
            }
        });

        const listMaterials = async (search=null) => {
            const filter = {
                type: state.materialType || '',
            }
            const response = await ItemApi.listItems(5, 0, search, filter);
            if (response) {
                state.meta.materialChoices = response.results.map( x => ({
                    label: x.full_name, value: x.id,
                    type: x.type, figure: x.onhand_quantity_formatted + ' available'
                }));
            }
        }
        watch(()=> props.value, ()=> {
            state.materialList = props.value;
        });
        watch(()=> state.materialType, ()=> {
            listMaterials();
        });

        return {
            state, listMaterials
        }
    }
}
</script>