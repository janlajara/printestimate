<template>
    <div>
        <Table :headers="['Name', 'Options', '']"
            layout="fixed" :cols-width="['', 'w-1/2', 'w-1/5']">
            <Row v-for="(x, i) in state.operationList" :key="i"
                    :class="state.operationForm.editIndex == i? 
                        'bg-secondary-light bg-opacity-20' : ''">
                <Cell>{{x.name}}</Cell>
                <Cell>
                    <span>{{x.optionsType}} select:</span>
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
            <InputCheckBox label="Is Required" 
                :value="state.operationForm.isRequired"
                @input="value => state.operationForm.isRequired = value"/>
            <InputTextLookup name="Operation Options" class="col-span-3" 
                multiple placeholder="Search..." :text="state.operationForm.lookupText"
                @select="(value)=>state.operationForm.metaOperationOptions = 
                    value.constructor === Array ? value : [value]"
                @input="value => state.operationForm.lookupText = value"
                :options="state.meta.metaOperationOptionChoices
                    .map(option=>({
                        value: option.value,
                        title: option.label,
                        isSelected: state.operationForm.metaOperationOptions.includes(option.value)}))
                    .filter(option => 
                        option.title.includes(state.operationForm.lookupText) ||
                        option.isSelected)
            "/>
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
import InputTextLookup from '@/components/InputTextLookup.vue';
import InputCheckBox from '@/components/InputCheckbox.vue';
import Table from '@/components/Table.vue';
import Row from '@/components/Row.vue';
import Cell from '@/components/Cell.vue';
import Button from '@/components/Button.vue';

import {reactive, computed, watch} from 'vue';
import {OperationApi} from '@/utils/apis.js';

export default {
    components: {
        InputText, InputSelect, InputTextLookup, InputCheckBox,
        Table, Row, Cell, Button
    },
    props: {
        materialType: String,
        costingMeasure: String,
        optionTypeChoices: Array,
        value: Array
    },
    emits: ['input'],
    setup(props, {emit}) {
        const state = reactive({
            materialType: computed(()=> props.materialType),
            costingMeasure: computed(()=> props.costingMeasure),
            optionTypeChoices: computed(()=> props.optionTypeChoices),
            operationList: [],
            operationForm: {
                id: null,
                editIndex: null,
                name: '',
                optionsType: '', 
                isRequired: false,
                lookupText: '',
                metaOperationOptions: []
            },
            meta: {
                metaOperationOptionChoices: [],
            },
            clearOperationForm: ()=> {
                state.operationForm = {
                    id: null,
                    editIndex: null,
                    name: '',
                    optionsType: '', 
                    isRequired: false,
                    lookupText: '',
                    metaOperationOptions: []
                }
            },
            saveOperation: ()=> {
                const editIndex = state.operationForm.editIndex;
                const operationForm = {
                    id: state.operationForm.id,
                    name: state.operationForm.name,
                    optionsType: state.operationForm.optionsType,
                    isRequired: state.operationForm.isRequired,
                    metaOperationOptions: state.operationForm.metaOperationOptions.map( x=> ({
                        operation: x,
                        label: state.meta.metaOperationOptionChoices.find(y => y.value == x).label
                    }))
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
                    isRequired: selected.isRequired,
                    operationForm: '',
                    metaOperationOptions: selected.metaOperationOptions.map( x => x.operation)
                }
                listOperations();
            },
            removeOperation: (index)=> {
                state.operationList.splice(index, 1)
            }
        });

        const listOperations = async () => {
            const filter = {
                material_type: state.materialType || '',
                costing_measure: state.costingMeasure || ''
            } 
            const response = await OperationApi.listOperations(filter);
            if (response) {
                state.meta.metaOperationOptionChoices = response
                    .sort((a,b)=> a.name > b.name)
                    .map( x => ({label: x.name, value: x.id}));
            }
        } 
        watch(()=> props.value, ()=> {
            state.operationList = props.value;

            listOperations();
        })
        watch(()=> props.costingMeasure, ()=> {
            listOperations();
        })

        return {
            state, listOperations
        }
    }
}
</script>