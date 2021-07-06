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

import {reactive, computed, watch, inject} from 'vue';
import {ActivityExpenseApi} from '@/utils/apis.js';

export default {
    components: {
        Modal, Section, InputText, InputSelect
    },
    props: {
        isOpen: Boolean,
        activityExpenseId: Number,
        onAfterSave: Function
    },
    emits: ['toggle'],
    setup(props) {
        const currency = inject('currency')
        const state = reactive({
            id: props.activityExpenseId,
            isCreate: computed(()=> state.id == null),
            isProcessing: false,
            error: '',
            data: {
                name: '', type: '', rate: ''
            },
            meta: {
                typeChoices: []
            },
            validate: ()=> {},
            save: ()=> {}
        })

        const retrieveActivityExpense = (id) => {
            state.isProcessing = true;
            if (id) {
                const response = ActivityExpenseApi.retrieveActivityExpense(id);
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

        const retrieveMetaData = () => {  
            if (state.id) {
                const response = ActivityExpenseApi.retrieveActivityExpense(state.id, true);
                console.log(response);
                state.meta.typeChoices = response.actions.PUT.type.choices.map(c=> ({
                    value: c.value, label: c.display_name
                }));
            }
        }

        watch(()=> props.isOpen, ()=> {
            if (!state.isCreate) retrieveActivityExpense(state.id);
            retrieveMetaData();
        })

        return {
            state, currency
        }
    }
}
</script>