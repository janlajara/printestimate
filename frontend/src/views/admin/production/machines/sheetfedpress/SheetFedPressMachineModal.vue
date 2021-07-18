<template>
    <Modal :heading="`${state.isCreate ? 'Add' : 'Edit'} Machine`" 
        :is-open="$props.isOpen" @toggle="(value)=> $emit('toggle', value)"
        :buttons="[{color: 'primary', icon:'save', text:'Save', 
            action: state.save, disabled: state.isProcessing},]">
        <div v-if="state.error" 
            class="pt-4 text-sm text-red-600">*{{state.error}}</div>
        <Section heading="General Information" heading-position="side"> 
            <div class="md:grid md:gap-4 md:grid-cols-3">
                <InputText name="Name"  placeholder="Name" class="md:col-span-2"
                    type="text" :value="state.data.name" required
                    @input="value => state.data.name = value"/>
                <InputSelect name="Type" required 
                    @input="(value)=>state.data.type = value"
                    :options="state.meta.machineTypes.map(c=>({
                        value: c.value, label: c.label,
                        isSelected: state.data.type == c.value
                    }))"/>
                <InputText name="Description"  placeholder="Description"  class="md:col-span-3"
                    type="text" :value="state.data.description" required
                    @input="value => state.data.description = value"/>
            </div>
        </Section>
        <Section heading="Sheet Length" heading-position="side"> 
            <div class="md:grid md:gap-4 md:grid-cols-3">
                <InputText name="Min" 
                    :max="state.data.maxLength"
                    placeholder="Min" :postfix="state.data.uom"
                    type="decimal" :value="state.data.minLength" required
                    @input="value => state.data.minLength = parseFloat(value)"/>
                <InputText name="Max"  
                    :min="state.data.minLength"
                    placeholder="Max" :postfix="state.data.uom"
                    type="decimal" :value="state.data.maxLength" required
                    @input="value => state.data.maxLength = parseFloat(value)"/>
                <InputSelect name="Unit" required :disabled="!state.isCreate"
                    @input="(value)=>state.data.uom = value"
                    :options="state.meta.uoms.map(c=>({
                        value: c.value, label: c.label,
                        isSelected: state.data.uom == c.value
                    }))"/>
            </div>
        </Section>
        <Section heading="Sheet Width" heading-position="side"> 
            <div class="md:grid md:gap-4 md:grid-cols-3">
                <InputText name="Min"  
                    :max="state.data.maxWidth"
                    placeholder="Min" :postfix="state.data.uom"
                    type="decimal" :value="state.data.minWidth" required
                    @input="value => state.data.minWidth = value"/>
                <InputText name="Max" 
                    :min="state.data.minWidth"
                    placeholder="Max" :postfix="state.data.uom"
                    type="decimal" :value="state.data.maxWidth" required
                    @input="value => state.data.maxWidth = value"/>
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
import {SheetFedPressMachineApi} from '@/utils/apis.js';

export default {
    components: {
        Modal, Section, InputText, InputSelect
    },
    props: {
        isOpen: Boolean,
        machineId: String,
        onAfterSave: Function
    },
    emits: ['toggle'],
    setup(props, {emit}) {
        const state = reactive({
            id: props.machineId,
            isCreate: computed(()=> props.machineId == null),
            isProcessing: false,
            error: '',
            data: {
                name: '', description: '', type: '', uom: '',
                minLength: 0, maxLength: 0,
                minWidth: 0, maxWidth: 0,
            },
            meta: {
                machineTypes: [],
                uoms: [],
                minParentSheetLength: null,
                minParentSheetWidth: null
            },
            clear: ()=> {
                state.data = {
                    name: '', description: '', type: '', uom: '',
                    minLength: 0, maxLength: 0,
                    minWidth: 0, maxWidth: 0,
                }
            },
            validate: ()=> {
                let errors = [];
                state.error = '';
                if (state.data.name == '') errors.push('name');
                if (state.data.type == '') errors.push('type');
                if (errors.length > 0) {
                    state.error = `The following fields must not be empty: ${errors.join(', ')}.`;
                    return true;
                }
                if (state.meta.minParentSheetLength && state.meta.minParentSheetWidth && 
                        (state.data.maxLength < state.meta.minParentSheetLength ||
                        state.data.maxWidth < state.meta.minParentSheetWidth)) {
                    state.error = `Sheet sizes must not be smaller than the smallest parent sheet: ` +
                        `${state.meta.minParentSheetWidth} x ${state.meta.minParentSheetWidth} ${state.data.uom}`;
                    return true;
                }
            },
            save: ()=> {
                if (state.validate()) return;
                const machine = {
                    name: state.data.name, description: state.data.description,
                    process_type: state.data.type, uom: state.data.uom,
                    min_sheet_length: state.data.minLength, 
                    max_sheet_length: state.data.maxLength,
                    min_sheet_width: state.data.minWidth,
                    max_sheet_width: state.data.maxWidth}
                saveMachine(machine);
            }
        });

        const retrieveMachine = async (id)=> {
            state.isProcessing = true;
            const response = await SheetFedPressMachineApi.retrieveSheetFedPressMachine(id);
            if (response) {
                state.data = {
                    name: response.name, description: response.description,
                    type: response.process_type, uom: response.uom,
                    minLength: response.min_sheet_length, maxLength: response.max_sheet_length, 
                    minWidth: response.min_sheet_width, maxWidth: response.max_sheet_width}
                state.meta.minParentSheetLength = response.min_parent_sheet_length
                state.meta.minParentSheetWidth = response.min_parent_sheet_width
            }
            state.isProcessing = false;
        }

        const retrieveMetaData = async ()=> {
            state.isProcessing = true;
            const response = await SheetFedPressMachineApi.listSheetFedPressMachines(true);
            if (response) {
                state.meta.machineTypes = response.actions.POST.process_type.choices.map(obj => ({
                    value: obj.value, label: obj.display_name
                }));
                state.meta.uoms = response.actions.POST.uom.choices.map(obj => ({
                    value: obj.value, label: obj.display_name
                }));
            }
            state.isProcessing = false;
        }

        const saveMachine = async (machine)=> {
            state.isProcessing = true;
            if (machine) {
                let response = null;
                if (!state.isCreate && state.id) {
                    response = await SheetFedPressMachineApi.updateSheetFedPressMachine(
                        state.id, machine);
                } else {
                    response = await SheetFedPressMachineApi.createSheetFedPressMachine(machine);
                }
                if (response) {
                    if (props.onAfterSave) props.onAfterSave();
                    emit('toggle', false);
                }
            }
            state.isProcessing = false;
        }

        watch(()=> props.isOpen, ()=> { 
            if (props.isOpen && state.id && !state.isCreate) {
                const id = parseInt(state.id);
                retrieveMachine(id);
            }
            if (!props.isOpen) state.clear();
            else state.error = '';
        })

        onBeforeMount(retrieveMetaData);

        return {
            state
        }
    }
}
</script>