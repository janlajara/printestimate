<template>
    <div>
        <Table :headers="['Name', 'Costing Measure', 'Options Type', 'Options', '']"
            layout="fixed" :cols-width="['', '', '', 'w-1/3', 'w-1/5']">
            <Row v-for="(x, i) in state.propertyList" :key="i"
                    :class="state.propertyForm.editIndex == i? 
                        'bg-secondary-light bg-opacity-20' : ''">
                <Cell>{{x.name}}</Cell>
                <Cell class="capitalize">{{x.costingMeasure}}</Cell>
                <Cell>{{x.optionsType}}</Cell>
                <Cell>
                    <ul class="pl-2">
                        <li v-for="(x, i) in x.metaPropertyOptions" :key="i"
                            class="list-disc">
                            {{x.label || x.id}}
                        </li>
                    </ul>
                </Cell>
                <Cell class="lg:px-0">
                    <div class="flex justify-end">
                        <Button class="my-auto px-0" icon="edit"
                            @click="()=>{state.editProperty(i)}"/>
                        <Button class="my-auto px-0" icon="clear" 
                            @click="()=>{state.removeProperty(i)}"/>
                    </div>
                </Cell>
            </Row>
        </Table>
        <hr/>
        <div class="md:grid md:gap-4 md:grid-cols-3">
            <InputText name="Name" required
                type="text" :value="state.propertyForm.name"
                @input="value => state.propertyForm.name = value"/>
            <InputSelect name="Costing Measure" required
                @input="(value)=> {
                    state.propertyForm.costingMeasure = value;
                    listOperations();
                    state.propertyForm.metaPropertyOptions = [];
                }"
                :options="state.meta.costingMeasureChoices.map(c=>({
                    value: c.value, label: c.label,
                    isSelected: state.propertyForm.costingMeasure == c.value
                }))"/>
            
            <InputCheckBox label="Is Required" 
                :value="state.propertyForm.isRequired"
                @input="value => state.propertyForm.isRequired = value"/>
            <InputSelect name="Options Type" required
                @input="(value)=>{
                    state.propertyForm.optionsType = value;
                    if (state.propertyForm.optionsType == 'Boolean') {
                        if (state.propertyForm.metaPropertyOptions.length > 0) {
                            state.propertyForm.metaPropertyOptions = 
                                [state.propertyForm.metaPropertyOptions[0]]
                        }
                    }
                }"
                :options="state.optionTypeChoices.map(c=>({
                    value: c.value, label: c.label,
                    isSelected: state.propertyForm.optionsType == c.value
                }))"/>
            <InputSelect name="Property Options" class="col-span-2"
                required :multiple="state.propertyForm.optionsType != 'Boolean'" 
                @input="(value)=>state.propertyForm.metaPropertyOptions = 
                    value.constructor === Array ? value : [value]"
                :options="state.meta.metaPropertyOptionChoices.map(c=>({
                    value: c.value, label: c.label,
                    isSelected: state.propertyForm.metaPropertyOptions.includes(c.value)
                }))"/> 
            <div class="flex justify-end col-span-3 mt-4 md:mt-0">
                <Button icon="add" class="my-auto border-gray-300 border"
                        @click="state.saveProperty">
                    {{ state.propertyForm.editIndex != null ? 'Update' : 'Add' }}</Button>
            </div>
        </div>
    </div>
</template>
<script>
import InputText from '@/components/InputText.vue';
import InputSelect from '@/components/InputSelect.vue';
import InputCheckBox from '@/components/InputCheckbox.vue';
import Table from '@/components/Table.vue';
import Row from '@/components/Row.vue';
import Cell from '@/components/Cell.vue';
import Button from '@/components/Button.vue';

import {reactive, computed, onBeforeMount, watch} from 'vue';
import {OperationApi} from '@/utils/apis.js';

export default {
    components: {
        InputText, InputSelect, InputCheckBox,
        Table, Row, Cell, Button
    },
    props: {
        materialType: String,
        optionTypeChoices: Array,
        value: Array
    },
    emits: ['input'],
    setup(props, {emit}) {
        const state = reactive({
            materialType: computed(()=> props.materialType),
            optionTypeChoices: computed(()=> props.optionTypeChoices),
            propertyList: [],
            propertyForm: {
                id: null,
                editIndex: null,
                name: '',
                optionsType: '', 
                costingMeasure: '',
                isRequired: false,
                metaPropertyOptions: []
            },
            meta: {
                materialTypeChoices: [],
                metaPropertyOptionChoices: [],
                costingMeasureChoicesMapping: [],
                costingMeasureChoices: computed(()=> {
                    const mapping =  state.meta.costingMeasureChoicesMapping.filter(
                        c => c.key == state.materialType);
                    if (mapping && mapping[0]) {
                        return mapping[0].value.map(c=> ({
                            value: c.value, label: c.display
                        }));
                    } else return [];
                }),
                costingMeasureChoice: computed(()=> {
                    const a = state.meta.costingMeasureChoicesMapping.find(
                        x => x.key == state.materialType);
                    if (a) return a.value.find(y => y.value == state.propertyForm.costingMeasure);
                    else return null;
                }),
            },
            clearPropertyForm: ()=> {
                state.propertyForm = {
                    id: null,
                    editIndex: null,
                    name: '',
                    optionsType: '', 
                    costingMeasure: '',
                    isRequired: false,
                    metaPropertyOptions: []
                }
            },
            saveProperty: ()=> {
                const editIndex = state.propertyForm.editIndex;
                const propertyForm = {
                    id: state.propertyForm.id,
                    name: state.propertyForm.name,
                    optionsType: state.propertyForm.optionsType,
                    costingMeasure: state.propertyForm.costingMeasure,
                    isRequired: state.propertyForm.isRequired,
                    metaPropertyOptions: state.propertyForm.metaPropertyOptions.map( x=> {
                        const o = state.meta.metaPropertyOptionChoices.find(y => y.value == x);
                        return {
                            id: o.id,
                            operation: x,
                            label: o.label
                        }
                    })
                };
                if (editIndex != null) {
                    state.propertyList[editIndex] = propertyForm;
                } else {
                    state.propertyList.push(propertyForm);
                }
                emit('input', state.propertyList);
                state.clearPropertyForm();
            },
            editProperty: (index)=> {
                const selected = state.propertyList[index];
                state.propertyForm = {
                    id: selected.id,
                    editIndex: index,
                    name: selected.name,
                    optionsType: selected.optionsType, 
                    costingMeasure: selected.costingMeasure,
                    isRequired: selected.isRequired,
                    metaPropertyOptions: selected.metaPropertyOptions.map( x => x.operation)
                }
                listOperations();
            },
            removeProperty: (index)=> {
                state.propertyList.splice(index, 1)
            }
        });

        const listOperationCostingMeasures = async () => {
            const response = await OperationApi.listOperationCostingMeasures();
            if (response) {
                state.meta.costingMeasureChoicesMapping = response.map(c=> ({
                    key: c.material, value:c.measure_choices
                }));
            }
        }

        const listOperations = async () => {
            const filter = {
                material_type: state.materialType || '',
                costing_measure: state.propertyForm.costingMeasure || ''
            }
            const response = await OperationApi.listOperations(filter);
            if (response) {
                state.meta.metaPropertyOptionChoices = response.map( x => ({
                    label: x.name, value: x.id
                }));
            }
        }
        onBeforeMount(listOperationCostingMeasures);
        watch(()=> props.value, ()=> {
            state.propertyList = props.value;
        })

        return {
            state, listOperations
        }
    }
}
</script>