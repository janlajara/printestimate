<template>
    <div>
        <Table :headers="['Name', 'Options Type', 'Options', '']"
            layout="fixed" :cols-width="['', '', 'w-1/3', 'w-1/5']">
            <Row v-for="(x, i) in state.propertyList" :key="i"
                    :class="state.propertyForm.editIndex == i? 
                        'bg-secondary-light bg-opacity-20' : ''">
                <Cell>{{x.name}}</Cell>
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
            <InputCheckBox label="Is Required" 
                :value="state.propertyForm.isRequired"
                @input="value => state.propertyForm.isRequired = value"/>
            <InputSelect name="Property Options" class="col-span-3"
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

import {reactive, computed, watch} from 'vue';
import {OperationApi} from '@/utils/apis.js';

export default {
    components: {
        InputText, InputSelect, InputCheckBox,
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
                metaPropertyOptionChoices: []
            },
            clearPropertyForm: ()=> {
                state.propertyForm = {
                    id: null,
                    editIndex: null,
                    name: '',
                    optionsType: '', 
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
                    isRequired: state.propertyForm.isRequired,
                    metaPropertyOptions: state.propertyForm.metaPropertyOptions.map( x=> ({
                        operation: x,
                        label: state.meta.metaPropertyOptionChoices.find(y => y.value == x).label
                    }))
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
                    isRequired: selected.isRequired,
                    metaPropertyOptions: selected.metaPropertyOptions.map( x => x.operation)
                }
                listOperations();
            },
            removeProperty: (index)=> {
                state.propertyList.splice(index, 1)
            }
        });

        const listOperations = async () => {
            const filter = {
                material_type: state.materialType || '',
                costing_measure: state.costingMeasure || ''
            }
            const response = await OperationApi.listOperations(filter);
            if (response) {
                state.meta.metaPropertyOptionChoices = response.map( x => ({
                    label: x.name, value: x.id
                }));
            }
        }
        watch(()=> props.value, ()=> {
            state.propertyList = props.value;
            listOperations();
        })

        return {
            state
        }
    }
}
</script>