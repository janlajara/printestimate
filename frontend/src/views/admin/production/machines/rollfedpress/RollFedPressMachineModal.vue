<template>
    <Modal :heading="`${state.isCreate ? 'Add' : 'Edit'} Roll-fed Press`" 
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
                <InputSelect name="Unit" required :disabled="!state.isCreate"
                    @input="(value)=>state.data.uom = value"
                    :options="state.meta.uoms.map(c=>({
                        value: c.value, label: c.label,
                        isSelected: state.data.uom == c.value
                    }))"/>
            </div>
        </Section>
        <hr/>
        <Section heading="Roll Width" heading-position="side"> 
            <div class="md:grid md:gap-4 md:grid-cols-3">
                <InputText name="Min"
                    :max="state.data.maxWidth"
                    placeholder="Min" :postfix="state.data.uom"
                    type="decimal" :value="state.data.minWidth" required
                    @input="value => state.data.minWidth = parseFloat(value)"/>
                <InputText name="Max" 
                    :min="state.data.minWidth"
                    placeholder="Max" :postfix="state.data.uom"
                    type="decimal" :value="state.data.maxWidth" required
                    @input="value => state.data.maxWidth = parseFloat(value)"/>
            </div>
        </Section>
        <hr/>
        <Section heading="Breakpoint Length" heading-position="side"> 
            <div class="md:grid md:gap-4 md:grid-cols-3">
                <InputText name="Min" 
                    :max="state.data.maxBreakpointLength"
                    placeholder="Min" :postfix="state.data.uom"
                    type="decimal" :value="state.data.minBreakpointLength" required
                    @input="value => state.data.minBreakpointLength = parseFloat(value)"/>
                <InputText name="Max"  
                    :min="state.data.minBreakpointLength"
                    placeholder="Max" :postfix="state.data.uom"
                    type="decimal" :value="state.data.maxBreakpointLength" required
                    @input="value => state.data.maxBreakpointLength = parseFloat(value)"/>
            </div>
        </Section>
        <hr/>
        <Section heading="Make-ready Spoilage" heading-position="side"> 
            <div class="md:grid md:gap-4 md:grid-cols-3">
                <InputText name="Spoilage length" 
                    placeholder="Min" :postfix="state.data.uom"
                    type="decimal" :value="state.data.makeReadySpoilageLength" required
                    @input="value => state.data.makeReadySpoilageLength = parseFloat(value)"/>
            </div>
        </Section>
        <hr/>
        <Section heading="Margins" heading-position="side"> 
            <div class="md:grid md:gap-4 md:grid-cols-3">
                <InputText name="Horizontal Margin" 
                    :min="0" :max="state.data.minWidth / 2"
                    placeholder="Min" :postfix="state.data.uom"
                    type="decimal" :value="state.data.horizontalMargin" required
                    @input="value => state.data.horizontalMargin = parseFloat(value)"/>
                <InputText name="Vertical Margin"  
                    :min="0"
                    placeholder="Max" :postfix="state.data.uom"
                    type="decimal" :value="state.data.verticalMargin" required
                    @input="value => state.data.verticalMargin = parseFloat(value)"/>
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
import {RollFedPressMachineApi} from '@/utils/apis.js';

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
                minWidth: 0, maxWidth: 0,
                minBreakpointLength: 0, 
                maxBreakpointLength: 0,
                makeReadySpoilageLength: 0,
                verticalMargin: 0, horizontalMargin: 0
            },
            meta: {
                machineTypes: [],
                uoms: []
            },
            clear: ()=> {
                state.data = {
                    name: '', description: '', type: '', uom: '',
                    minWidth: 0, maxWidth: 0,
                    minBreakpointLength: 0, 
                    maxBreakpointLength: 0,
                    makeReadySpoilageLength: 0,
                    verticalMargin: 0, horizontalMargin: 0
                }
            },
            validate: ()=> {
                let errors = [];
                state.error = '';
                if (state.data.name == '') errors.push('name');
                if (state.data.type == '') errors.push('type');
                if (state.data.uom == '') errors.push('uom');
                if (errors.length > 0) {
                    state.error = `The following fields must not be empty: ${errors.join(', ')}.`;
                    return true;
                }
            },
            save: ()=> {
                if (state.validate()) return;
                const machine = {
                    name: state.data.name, description: state.data.description,
                    process_type: state.data.type, uom: state.data.uom,
                    min_sheet_width: state.data.minWidth,
                    max_sheet_width: state.data.maxWidth,
                    min_sheet_breakpoint_length: state.data.minBreakpointLength, 
                    max_sheet_breakpoint_length: state.data.maxBreakpointLength,
                    make_ready_spoilage_length: state.data.makeReadySpoilageLength,
                    vertical_margin: state.data.verticalMargin,
                    horizontal_margin: state.data.horizontalMargin}
                saveMachine(machine);
            }
        });

        const retrieveMachine = async (id)=> {
            state.isProcessing = true;
            const response = await RollFedPressMachineApi.retrieveRollFedPressMachine(id);
            if (response) {
                state.data = {
                    name: response.name, description: response.description,
                    type: response.process_type, uom: response.uom,
                    minWidth: response.min_sheet_width, 
                    maxWidth: response.max_sheet_width,
                    minBreakpointLength: response.min_sheet_breakpoint_length, 
                    maxBreakpointLength: response.max_sheet_breakpoint_length,
                    makeReadySpoilageLength: response.make_ready_spoilage_length,
                    verticalMargin: response.vertical_margin,
                    horizontalMargin: response.horizontal_margin}
            }
            state.isProcessing = false;
        }

        const retrieveMetaData = async ()=> {
            state.isProcessing = true;
            const response = await RollFedPressMachineApi.listRollFedPressMachines(true);
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
                    response = await RollFedPressMachineApi.updateRollFedPressMachine(
                        state.id, machine);
                } else {
                    response = await RollFedPressMachineApi.createRollFedPressMachine(machine);
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