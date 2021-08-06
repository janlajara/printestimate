<template>
    <Modal :heading="`${state.isCreate ? 'Add' : 'Edit'} Workstation`" 
        :is-open="$props.isOpen" @toggle="(value)=> $emit('toggle', value)"
        :buttons="[{color: 'primary', icon:'save', text:'Save', 
            action: state.save, disabled: state.isProcessing},]">
        <div v-if="state.error" 
            class="pt-4 text-sm text-red-600">*{{state.error}}</div>
        <Section heading="General Information" heading-position="side"> 
            <div class="md:grid md:gap-4 md:grid-cols-3">
                <InputText name="Name"  placeholder="Name" class="col-span-2"
                    type="text" :value="state.data.name" required
                    @input="value => state.data.name = value"/>
                <InputSelect name="Machine" :disabled="!state.meta.isMachineEditable"
                    @input="(value)=>state.data.machine = value"
                    :options="state.meta.machines.map(c=>({
                        value: c.value, label: c.label,
                        isSelected: state.data.machine == c.value
                    }))"/>
                <InputText name="Description"  placeholder="Description"  class="col-span-2"
                    type="text" :value="state.data.description" required
                    @input="value => state.data.description = value"/>
            </div>
        </Section>
    </Modal>
</template>

<script>
import Modal from '@/components/Modal.vue';
import Section from '@/components/Section.vue';
import InputText from '@/components/InputText.vue';
import InputSelect from '@/components/InputSelect.vue';

import {reactive, computed, watch, onBeforeMount} from 'vue';
import {WorkstationApi, MachineApi} from '@/utils/apis.js';

export default {
    components: {
        Modal, Section, InputText, InputSelect
    },
    props: {
        isOpen: Boolean,
        workstationId: String,
        onAfterSave: Function
    },
    emits: ['toggle'],
    setup(props, {emit}) {
        const state = reactive({
            id: props.workstationId,
            isCreate: computed(()=> props.workstationId == null),
            isProcessing: false,
            error: '',
            data: {
                name: '', description: '', machine: null
            },
            meta: {
                machines: [],
                isMachineEditable: true,
            },
            clear: ()=> {
                state.data = {
                    name: '', description: '', machine: null
                }
            },
            validate: ()=> {
                let errors = [];
                if (state.data.name == '' || state.data.name == null) errors.push('name');
                if (errors.length > 0)
                    state.error = `The following fields must not be empty: ${errors.join(', ')}.`;
                else state.error = '';
                return errors.length > 0;
            },
            save: ()=> {
                if (state.validate()) return;
                const workstation = {
                    name: state.data.name, 
                    description: state.data.description,
                    machine: state.data.machine}
                saveWorkstation(workstation);
            }
        });

        const retrieveWorkstation = async (id)=> {
            state.isProcessing = true;
            const response = await WorkstationApi.retrieveWorkstation(id);
            if (response) {
                state.data = {
                    name: response.name, description: response.description,
                    machine: response.machine
                }
                state.meta.isMachineEditable = response.can_edit_machine
            }
            state.isProcessing = false;
        }

        const retrieveMachines = async ()=> {
            const response = await MachineApi.listMachines();
            if (response) {
                state.meta.machines = response.map(x => ({
                    value: x.id, label: x.name
                }))
            }
        }

        const saveWorkstation = async (workstation)=> {
            state.isProcessing = true;
            if (workstation) {
                let response = null;
                if (!state.isCreate && state.id) {
                    response = await WorkstationApi.updateWorkstation(state.id, workstation);
                } else {
                    response = await WorkstationApi.createWorkstation(workstation);
                }
                if (response) {
                    if (props.onAfterSave) props.onAfterSave();
                    emit('toggle', false);
                }
            }
            state.isProcessing = false;
        }

        watch(()=> props.isOpen, ()=> { 
            if (props.isOpen) {
                state.clear();
                if (state.id && !state.isCreate) {
                    const id = parseInt(state.id);
                    retrieveWorkstation(id);
                }
            }
        })

        onBeforeMount(retrieveMachines);

        return {
            state
        }
    }
}
</script>