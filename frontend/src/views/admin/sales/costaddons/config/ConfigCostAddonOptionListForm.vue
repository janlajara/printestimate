<template>
    <div>
        <Table :headers="['Label', 'Value', '']"
            layout="fixed" :cols-width="['', 'w-1/2', 'w-1/5']">
            <Row v-for="(x, i) in state.optionList" :key="i"
                    :class="state.optionList.editIndex == i? 
                        'bg-secondary-light bg-opacity-20' : ''">
                <Cell>{{x.label}}</Cell>
                <Cell>{{x.value}} {{state.meta.symbol}}</Cell>
                <Cell class="lg:px-0">
                    <div class="flex justify-end">
                        <Button class="my-auto px-0" icon="edit"
                            @click="()=>{state.editOption(i)}"/>
                        <Button class="my-auto px-0" icon="clear" 
                            @click="()=>{state.removeOption(i)}"/>
                    </div>
                </Cell>
            </Row>
        </Table>
        <hr/>
        <div v-if="state.error" 
            class="pt-4 text-sm text-red-600">*{{state.error}}</div>
        <div class="md:grid md:gap-4 md:grid-cols-3">
            <InputText name="Label" required
                type="text" :value="state.optionForm.label"
                @input="value => state.optionForm.label = value"/>
            <InputText name="Value" required
                type="decimal" :value="state.optionForm.value"
                :postfix="state.meta.symbol"
                @input="value => state.optionForm.value = value"/>
            <div class="flex justify-end col-span-3 mt-4 md:mt-0">
                <Button icon="add" class="my-auto border-gray-300 border"
                        @click="state.saveOption">
                    {{ state.optionForm.editIndex != null ? 'Update' : 'Add' }}</Button>
            </div>
        </div>
    </div>
</template>
<script>
import InputText from '@/components/InputText.vue';
import Table from '@/components/Table.vue';
import Row from '@/components/Row.vue';
import Cell from '@/components/Cell.vue';
import Button from '@/components/Button.vue';

import {reactive, computed, watch, inject} from 'vue';

export default {
    components: {
        InputText, Table, Row, Cell, Button
    },
    props: {
        type: String,
        value: Array
    },
    emits: ['input'],
    setup(props, {emit}) {
        const currency = inject('currency').abbreviation;
        const state = reactive({
            error: null,
            optionList: [],
            optionForm: {
                id: null,
                editIndex: null,
                label: '',
                value: ''
            },
            meta: {
                symbol: computed(()=> props.type == 'percentage'? '%': currency)
            },
            validate: ()=> {
                let errors = [];
                if (state.optionForm.label == '') errors.push('label');
                if (state.optionForm.value == null || 
                    state.optionForm.value == '') errors.push('value');
                if (errors.length > 0)
                    state.error = `The following fields must not be empty: ${errors.join(', ')}.`;
                else state.error = '';
                return errors.length > 0;
            },
            clearOptionForm: ()=> {
                state.optionForm = {
                    id: null,
                    editIndex: null,
                    label: '',
                    value: '' }
            },
            saveOption: ()=> {                
                if (state.validate()) return;
                const editIndex = state.optionForm.editIndex;
                const optionForm = {
                    id: state.optionForm.id,
                    label: state.optionForm.label,
                    value: state.optionForm.value
                };
                if (editIndex != null) {
                    state.optionList[editIndex] = optionForm;
                } else {
                    state.optionList.push(optionForm);
                }
                emit('input', state.optionList);
                state.clearOptionForm();
            },
            editOption: (index)=> {
                const selected = state.optionList[index];
                state.optionForm = {
                    id: selected.id,
                    editIndex: index,
                    label: selected.label,
                    value: selected.value
                }
            },
            removeOption: (index)=> {
                state.optionList.splice(index, 1)
            }
        });

        watch(()=> props.value, ()=> {
            state.optionList = props.value;
        })

        return {
            state
        }
    }
}
</script>