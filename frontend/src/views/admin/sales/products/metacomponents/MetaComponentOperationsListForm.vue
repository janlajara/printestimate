<template>
    <div>
        <Table :headers="['Name', 'Costing Measure', 'Options Type', 'Options', '']"
            layout="fixed" :cols-width="['', '', '', 'w-1/3', 'w-1/5']">
            <Row v-for="(x, i) in state.operationList" :key="i"
                    :class="state.operationForm.editIndex == i? 
                        'bg-secondary-light bg-opacity-20' : ''">
                <Cell>{{x.name}}</Cell>
                <Cell class="capitalize">{{x.costingMeasure}}</Cell>
                <Cell>{{x.optionsType}}</Cell>
                <Cell>
                    <ul class="pl-2">
                        <li v-for="(x, i) in x.metaOperationOptions" :key="i"
                            class="list-disc">
                            {{x.label || x.id}}
                        </li>
                    </ul>
                </Cell>
                <Cell class="lg:px-0">
                    <div class="flex justify-end">
                        <Button class="my-auto px-0" icon="edit"
                            @click="()=>{state.editOperation(i)}"/>
                        <Button class="my-auto px-0" icon="clear" 
                            @click="()=>{state.removeOperation(i)}"/>
                    </div>
                </Cell>
            </Row>
        </Table>
        <hr/>
        <div class="md:grid md:gap-4 md:grid-cols-3">
            <InputText name="Name" required
                type="text" :value="state.operationForm.name"
                @input="value => state.operationForm.name = value"/>
            <InputSelect name="Costing Measure" required
                @input="(value)=> {
                    state.operationForm.costingMeasure = value;
                    listOperations();
                    state.operationForm.metaOperationOptions = [];
                }"
                :options="state.meta.costingMeasureChoices.map(c=>({
                    value: c.value, label: c.label,
                    isSelected: state.operationForm.costingMeasure == c.value
                }))"/>
            
            <InputCheckBox label="Is Required" 
                :value="state.operationForm.isRequired"
                @input="value => state.operationForm.isRequired = value"/>
            <InputSelect name="Options Type" required
                @input="(value)=>{
                    state.operationForm.optionsType = value;
                    if (state.operationForm.optionsType == 'Boolean') {
                        if (state.operationForm.metaOperationOptions.length > 0) {
                            state.operationForm.metaOperationOptions = 
                                [state.operationForm.metaOperationOptions[0]]
                        }
                    }
                }"
                :options="state.optionTypeChoices.map(c=>({
                    value: c.value, label: c.label,
                    isSelected: state.operationForm.optionsType == c.value
                }))"/>
            <InputSelect name="Operation Options" class="col-span-2"
                required :multiple="state.operationForm.optionsType != 'Boolean'" 
                @input="(value)=>state.operationForm.metaOperationOptions = 
                    value.constructor === Array ? value : [value]"
                :options="state.meta.metaOperationOptionChoices.map(c=>({
                    value: c.value, label: c.label,
                    isSelected: state.operationForm.metaOperationOptions.includes(c.value)
                }))"/> 
            <div class="flex justify-end col-span-3 mt-4 md:mt-0">
                <Button icon="add" class="my-auto border-gray-300 border"
                        @click="state.saveOperation">
                    {{ state.operationForm.editIndex != null ? 'Update' : 'Add' }}</Button>
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
            operationList: [],
            operationForm: {
                id: null,
                editIndex: null,
                name: '',
                optionsType: '', 
                costingMeasure: '',
                isRequired: false,
                metaOperationOptions: []
            },
            meta: {
                materialTypeChoices: [],
                metaOperationOptionChoices: [],
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
                    if (a) return a.value.find(y => y.value == state.operationForm.costingMeasure);
                    else return null;
                }),
            },
            clearOperationForm: ()=> {
                state.operationForm = {
                    id: null,
                    editIndex: null,
                    name: '',
                    optionsType: '', 
                    costingMeasure: '',
                    isRequired: false,
                    metaOperationOptions: []
                }
            },
            saveOperation: ()=> {
                const editIndex = state.operationForm.editIndex;
                const operationForm = {
                    id: state.operationForm.id,
                    name: state.operationForm.name,
                    optionsType: state.operationForm.optionsType,
                    costingMeasure: state.operationForm.costingMeasure,
                    isRequired: state.operationForm.isRequired,
                    metaOperationOptions: state.operationForm.metaOperationOptions.map( x=> {
                        const o = state.meta.metaOperationOptionChoices.find(y => y.value == x);
                        return {
                            id: o.id,
                            operation: x,
                            label: o.label
                        }
                    })
                };
                if (editIndex != null) {
                    state.operationList[editIndex] = operationForm;
                } else {
                    state.operationList.push(operationForm);
                }
                emit('input', state.operationList);
                state.clearOperationForm();
            },
            editOperation: (index)=> {
                const selected = state.operationList[index];
                state.operationForm = {
                    id: selected.id,
                    editIndex: index,
                    name: selected.name,
                    optionsType: selected.optionsType, 
                    costingMeasure: selected.costingMeasure,
                    isRequired: selected.isRequired,
                    metaOperationOptions: selected.metaOperationOptions.map( x => x.operation)
                }
                listOperations();
            },
            removeOperation: (index)=> {
                state.operationList.splice(index, 1)
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
                costing_measure: state.operationForm.costingMeasure || ''
            }
            const response = await OperationApi.listOperations(filter);
            if (response) {
                state.meta.metaOperationOptionChoices = response.map( x => ({
                    label: x.name, value: x.id
                }));
            }
        }
        onBeforeMount(listOperationCostingMeasures);
        watch(()=> props.value, ()=> {
            state.operationList = props.value;
        })

        return {
            state, listOperations
        }
    }
}
</script>