<template>
    <Modal :heading="`${state.isCreate ? 'Add' : 'Edit'} Activity Expense`" 
        :is-open="$props.isOpen" @toggle="(value)=> $emit('toggle', value)"
        :buttons="[{color: 'primary', icon:'save', text:'Save', 
            action: state.save, disabled: state.isProcessing},]">
        <div v-if="state.error" 
            class="pt-4 text-sm text-red-600">*{{state.error}}</div>
        <Section heading="General Information" heading-position="side"> 
            <div class="md:grid md:gap-4 md:grid-cols-3">
                <InputText name="Name"  placeholder="Name"
                    type="text" :value="state.data.name" required
                    @input="value => state.data.name = value"/>
                <InputSelect name="Type" required
                    @input="(value)=>state.data.type = value"
                    :options="state.meta.typeChoices.map(c=>({
                        value: c.value, label: c.label,
                        isSelected: state.data.type == c.value
                    }))"/>
                <InputText type="money" name="Rate" required
                    :prefix="currency.symbol"
                    @input="(value)=> state.data.rate = value"
                    :value="state.data.rate"/>
            </div>
        </Section>
    </Modal>
</template>

<script>
import Modal from '@/components/Modal.vue';
import Section from '@/components/Section.vue';
import InputText from '@/components/InputText.vue';
import InputSelect from '@/components/InputSelect.vue';

import {reactive, computed, watch, inject, onBeforeMount} from 'vue';
import {WorkstationApi, ActivityExpenseApi} from '@/utils/apis.js';

export default {
    components: {
        Modal, Section, InputText, InputSelect
    },
    props: {
        isOpen: Boolean,
        activityExpenseId: Number,
        workstationId: Number,
        onAfterSave: Function
    },
    emits: ['toggle'],
    setup(props, {emit}) { 
        const currency = inject('currency');
        const state = reactive({
            id: computed(()=>props.activityExpenseId),
            workstationId: computed(()=>props.workstationId),
            isCreate: computed(()=> state.id == null),
            isProcessing: false,
            error: '',
            data: {
                name: '', type: '', rate: ''
            },
            meta: {
                typeChoices: []
            },
            clearData: ()=> {
                state.data = {name: '', type: '', rate: ''};
            },
            validate: ()=> {
                let errors = [];
                if (state.data.name == '' || state.data.name == null) errors.push('name');
                if (state.data.type == '' || state.data.type == null) errors.push('type');
                if (state.data.rate == '' || state.data.rate == null) errors.push('rate');
                if (errors.length > 0)
                    state.error = `The following fields must not be empty: ${errors.join(', ')}.`;
                else state.error = '';
                return errors.length > 0;
            },
            save: ()=> {
                if (state.validate()) return;
                const request = {
                    name: state.data.name,
                    type: state.data.type,
                    rate: state.data.rate
                }
                saveActivityExpense(request);
            }
        })

        const retrieveActivityExpense = async (id) => {
            state.isProcessing = true;
            if (id) {
                const response = await ActivityExpenseApi.retrieveActivityExpense(id);
                if (response) {
                    state.data = {
                        name: response.name, 
                        type: response.type, 
                        rate: response.rate
                    }
                }
            }
            state.isProcessing = false;
        }

        const retrieveMetaData = async () => {
            if (state.workstationId) {
                const response = await WorkstationApi.retrieveWorkstationActivityExpenses(
                    state.workstationId, true);
                state.meta.typeChoices = response.actions.POST.type.choices.map(c=> ({
                    value: c.value, label: c.display_name
                }));
            }
        }

        const saveActivityExpense = (activityExpense) => {
            state.isProcessing = true;
            let response = null;
            if (state.isCreate) {
                response = WorkstationApi.createWorkstationActivityExpense(
                    state.workstationId, activityExpense);
            } else {
                response = ActivityExpenseApi.updateActivityExpense(
                    state.id, activityExpense);
            }
            if (response) {
                if (props.onAfterSave) props.onAfterSave();
                emit('toggle', false)
            }
            state.isProcessing = false;
        }

        watch(()=> [props.isOpen], ()=> {
            if (props.isOpen) {
                if (!state.isCreate) retrieveActivityExpense(state.id);
                else state.clearData();
                state.error = '';
            }
        })
        onBeforeMount(()=> {
            retrieveMetaData();
        })

        return {
            state, currency
        }
    }
}
</script>