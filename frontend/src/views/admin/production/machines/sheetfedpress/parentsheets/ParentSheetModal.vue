<template>
    <Modal :heading="`${state.isCreate ? 'Add' : 'Edit'} Sheet`" 
        :is-open="$props.isOpen" 
        @toggle="(value)=> $emit('toggle', value)"
        :buttons="[{color: 'primary', icon:'save', text:'Save', 
            action: state.save, disabled: state.isProcessing},]">
        <div v-if="state.error" 
            class="pt-4 text-sm text-red-600">*{{state.error}}</div>
        <Section heading="Sheet Size" heading-position="side"> 
            <div class="md:grid md:gap-4 md:grid-cols-3">
                <InputText name="Width" 
                    :min="state.meta.sizeRestrictions.minWidth"
                    :max="state.meta.sizeRestrictions.maxWidth"
                    :postfix="state.meta.uom" type="decimal" 
                    :value="state.data.width" required
                    @input="value => state.data.width = 
                        value? parseFloat(value) : 0"/>
                <InputText name="Length" 
                    :min="state.meta.sizeRestrictions.minLength"
                    :max="state.meta.sizeRestrictions.maxLength"
                    :postfix="state.meta.uom" type="decimal" 
                    :value="state.data.length" required
                    @input="value => state.data.length = 
                        value? parseFloat(value) : 0"/>
                <InputText name="Size Name"  placeholder="Size Name" 
                    type="text" :value="state.data.label"
                    @input="value => state.data.label = value"
                    class="col-span-1"/>
            </div>
        </Section>
        <Section heading="Padding" heading-position="side"> 
            <div class="md:grid md:gap-4 md:grid-cols-4">
                <InputText name="Top" :disabled="!state.meta.sizeValid"
                    :max="state.meta.sizeRestrictions.maxPadTop"
                    :postfix="state.meta.uom" type="decimal" 
                    :value="state.data.paddingTop" 
                    @input="value => state.data.paddingTop = value? parseFloat(value) : 0"/>
                <InputText name="Right" :disabled="!state.meta.sizeValid"
                    :max="state.meta.sizeRestrictions.maxPadRight"
                    :postfix="state.meta.uom" type="decimal" 
                    :value="state.data.paddingRight" 
                    @input="value => state.data.paddingRight = value? parseFloat(value) : 0"/>
                <InputText name="Bottom" :disabled="!state.meta.sizeValid" 
                    :max="state.meta.sizeRestrictions.maxPadBottom"
                    :postfix="state.meta.uom" type="decimal" 
                    :value="state.data.paddingBottom" 
                    @input="value => state.data.paddingBottom = value? parseFloat(value) : 0"/>
                <InputText name="Left" :disabled="!state.meta.sizeValid"  
                    :max="state.meta.sizeRestrictions.maxPadLeft"
                    :postfix="state.meta.uom" type="decimal" 
                    :value="state.data.paddingLeft" 
                    @input="value => state.data.paddingLeft = value? parseFloat(value) : 0"/>
            </div>
        </Section>
        <Section heading="Layout" heading-position="side">
            <div class="mt-2 bg-gray-200 px-4 py-4 rounded-md">
                <Svg :svg-height="250"
                    :view-box-width="state.data.width" 
                    :view-box-height="state.data.length">
                    <ParentSheetShape
                        :display-label="true"
                        :width="state.data.width"
                        :length="state.data.length"
                        :padding-top="state.data.paddingTop"
                        :padding-right="state.data.paddingRight"
                        :padding-bottom="state.data.paddingBottom"
                        :padding-left="state.data.paddingLeft"/>
                </Svg>
            </div>
        </Section>
    </Modal>
</template>

<script>
import Modal from '@/components/Modal.vue';
import Section from '@/components/Section.vue';
import InputText from '@/components/InputText.vue';
import Svg from '@/utils/svg/Svg.vue';
import ParentSheetShape from '@/views/admin/production/machines/sheetfedpress/parentsheets/ParentSheetShape.vue';

import {reactive, computed, watch} from 'vue';
import {ParentSheetApi, SheetFedPressMachineApi} from '@/utils/apis.js';

export default {
    components: {
        Modal, Section, InputText, Svg, ParentSheetShape
    },
    props: {
        isOpen: Boolean,
        parentSheetId: Number,
        machineId: String,
        onAfterSave: Function
    },
    emits: ['toggle'],
    setup(props, {emit}) {
        const state = reactive({
            id: computed(()=>props.parentSheetId),
            machineId: computed(()=>props.machineId),
            isCreate: computed(()=> state.id == null),
            isProcessing: false,
            error: '',
            data: {
                label: '', width: 0, length: 0, 
                paddingTop: 0, paddingRight: 0, 
                paddingBottom: 0, paddingLeft: 0
            },
            meta: {
                machine: null,
                uom: computed(()=> (state.meta.machine)? state.meta.machine.uom : ''),
                sizeValid: computed(()=> state.data.length != '' && state.data.width != ''),
                sizeRestrictions: computed(()=> ({
                    minLength: (state.meta.machine)? state.meta.machine.minLength : 0,
                    maxLength: (state.meta.machine)? state.meta.machine.maxLength : 0,
                    minWidth: (state.meta.machine)? state.meta.machine.minWidth : 0,
                    maxWidth: (state.meta.machine)? state.meta.machine.maxWidth : 0,
                    maxPadTop: (state.data.length > 0)? 
                        state.data.length - state.data.paddingBottom : 0,
                    maxPadRight: (state.data.width > 0)? 
                        state.data.width - state.data.paddingRight : 0,
                    maxPadBottom: (state.data.length > 0)? 
                        state.data.length - state.data.paddingTop : 0,
                    maxPadLeft: (state.data.width > 0)? 
                        state.data.width - state.data.paddingRight : 0,
                }))                
            },
            clearData: ()=> {
                state.data = {
                    label: '', width: 0, length: 0, uom: '',
                    paddingTop: 0, paddingRight: 0, 
                    paddingBottom: 0, paddingLeft: 0};
            },
            validate: ()=> {
                let errors = [];
                if (state.data.width == '') errors.push('width');
                if (state.data.length == '') errors.push('length');
                if (errors.length > 0)
                    state.error = `The following fields must not be empty: ${errors.join(', ')}.`;
                else state.error = '';
                return errors.length > 0;
            },
            save: ()=> {
                if (state.validate()) return;
                const request = {
                    label: state.data.label,
                    width_value: state.data.width,
                    length_value: state.data.length,
                    size_uom: state.meta.uom,
                    padding_top: state.data.paddingTop,
                    padding_right: state.data.paddingRight,
                    padding_bottom: state.data.paddingBottom,
                    padding_left: state.data.paddingLeft
                }
                saveParentSheet(request);
            }
        })

        const retrieveParentSheet = async (id) => {
            state.isProcessing = true;
            if (id) {
                const response = await ParentSheetApi.retrieveParentSheet(id);
                if (response) {
                    state.data = {
                        label: response.label, 
                        width: response.width_value, 
                        length: response.length_value, 
                        uom: response.size_uom,
                        paddingTop: response.padding_top, 
                        paddingRight: response.padding_right, 
                        paddingBottom: response.padding_bottom, 
                        paddingLeft: response.padding_left
                    }
                }
            }
            state.isProcessing = false;
        }

        const saveParentSheet = async (sheet) => {
            state.isProcessing = true;
            let response = null;
            if (state.isCreate) {
                response = await SheetFedPressMachineApi.createSheetFedPressMachineParentSheet(
                    state.machineId, sheet);
            } else {
                response = await ParentSheetApi.updateParentSheet(
                    state.id, sheet);
            }
            if (response) {
                if (props.onAfterSave) props.onAfterSave();
                emit('toggle', false)
            }
            state.isProcessing = false;
        }

        const retrieveSheetFedMachine = async (id)=> {
            state.isProcessing = true;
            if (props.machineId) {
                const response = await SheetFedPressMachineApi.retrieveSheetFedPressMachine(id);
                if (response) {
                    state.meta.machine = {
                        uom: response.uom,
                        minWidth: response.min_sheet_width,
                        maxWidth: response.max_sheet_width,
                        minLength: response.min_sheet_length,
                        maxLength: response.max_sheet_length
                    }
                }
            }
            state.isProcessing = false;
        }

        watch(()=> [props.isOpen], async ()=> {
            state.clearData()
            if (props.isOpen) {
                await retrieveSheetFedMachine(state.machineId);
                if (!state.isCreate) await retrieveParentSheet(state.id);
                state.error = '';
            }
        })

        return {
            state, 
        }
    }
}
</script>