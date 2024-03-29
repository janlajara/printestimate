<template>
    <Modal :heading="`${state.isCreate ? 'Add' : 'Edit'} Sheet`" 
        :is-open="$props.isOpen" 
        @toggle="(value)=> $emit('toggle', value)"
        :buttons="[{color: 'primary', icon:'save', text:'Save', 
            action: state.save, disabled: state.isProcessing},]">
        <div v-if="state.error" 
            class="pt-4 text-sm text-red-600">*{{state.error}}</div>
        <Section heading="Parent Sheet" heading-position="side"> 
            <div class="md:grid md:gap-4 md:grid-cols-2">
                <InputSelect name="Parent" required 
                    @input="(value)=>{
                        state.data.parent = value;}"
                    :options="state.meta.parentSheets.map(c=>({
                        value: c.id, label: c.label,
                        isSelected: state.data.parent == c.id
                    }))"/>
                <DescriptionItem 
                    name="Useable Area" :value="state.meta.parentPackSize || 0"/>
            </div>
        </Section>
        <Section heading="Sheet Size" heading-position="side"> 
            <div class="md:grid md:gap-4 md:grid-cols-3">
                <InputText name="Width" 
                    :max="state.meta.sizeRestrictions.maxWidth"
                    :postfix="state.meta.uom" type="decimal" 
                    :value="state.data.width" required
                    @input="value => {
                        state.data.width = value? parseFloat(value) : 0;
                        state.clearMarginData()}"/>
                <InputText name="Length" 
                    :max="state.meta.sizeRestrictions.maxLength"
                    :postfix="state.meta.uom" type="decimal" 
                    :value="state.data.length" required
                    @input="value => {
                        state.data.length = value? parseFloat(value) : 0
                        state.clearMarginData()}"/>
                <InputText name="Size Name"  placeholder="Size Name" 
                    type="text" :value="state.data.label"
                    @input="value => state.data.label = value"
                    class="col-span-1"/>
            </div>
        </Section>
        <Section heading="Margin" heading-position="side"> 
            <div class="md:grid md:gap-4 md:grid-cols-4">
                <InputText name="Top" :disabled="!state.meta.sizeValid"
                    :max="state.meta.sizeRestrictions.maxMarginTop"
                    :postfix="state.meta.uom" type="decimal" 
                    :value="state.data.marginTop" 
                    @input="value => state.data.marginTop = value? parseFloat(value) : 0"/>
                <InputText name="Right" :disabled="!state.meta.sizeValid"
                    :max="state.meta.sizeRestrictions.maxMarginRight"
                    :postfix="state.meta.uom" type="decimal" 
                    :value="state.data.marginRight" 
                    @input="value => state.data.marginRight = value? parseFloat(value) : 0"/>
                <InputText name="Bottom" :disabled="!state.meta.sizeValid" 
                    :max="state.meta.sizeRestrictions.maxMarginBottom"
                    :postfix="state.meta.uom" type="decimal" 
                    :value="state.data.marginBottom" 
                    @input="value => state.data.marginBottom = value? parseFloat(value) : 0"/>
                <InputText name="Left" :disabled="!state.meta.sizeValid"  
                    :max="state.meta.sizeRestrictions.maxMarginLeft"
                    :postfix="state.meta.uom" type="decimal" 
                    :value="state.data.marginLeft" 
                    @input="value => state.data.marginLeft = value? parseFloat(value) : 0"/>
            </div>
        </Section>
        <Section heading="Layout" heading-position="side">
            <ul class="my-3 flex gap-6">
                <li v-for="(tab, index) in ['Any Direction', 'Fixed Direction']" :key="index"
                    @click="()=> state.meta.layoutRotate = tab == 'Any Direction'"
                    class="tab cursor-pointer" 
                    :class="!state.meta.layoutRotate && tab == 'Fixed Direction' || 
                            state.meta.layoutRotate && tab == 'Any Direction' ? 
                        'text-primary border-primary font-bold border-b-4' : 
                        ''">
                    {{tab}}
                </li>
            </ul>
            <div class="mt-2 bg-gray-200 px-4 py-4 rounded-md">
                <ChildSheetLayout 
                    v-if="state.meta.parentSheet"
                    :parent-width="state.meta.parentSheet.width"
                    :parent-length="state.meta.parentSheet.length"
                    :parent-uom="state.meta.parentSheet.uom"
                    :parent-padding-top="state.meta.parentSheet.paddingTop"
                    :parent-padding-right="state.meta.parentSheet.paddingRight"
                    :parent-padding-bottom="state.meta.parentSheet.paddingBottom"
                    :parent-padding-left="state.meta.parentSheet.paddingLeft"
                    :child-width="state.data.width"
                    :child-length="state.data.length"
                    :child-uom="state.meta.uom"
                    :child-margin-top="state.data.marginTop"
                    :child-margin-right="state.data.marginRight"
                    :child-margin-bottom="state.data.marginBottom"
                    :child-margin-left="state.data.marginLeft"
                    :allow-rotate="state.meta.layoutRotate"
                    @loaded="layout => state.meta.layout = layout"/>
            </div>
            <DescriptionList v-if="state.meta.layout">
                <div class="flex justify-between">
                    <DescriptionItem name="Yield" 
                        :value="`${state.meta.layout.count} sheets`"/>
                    <DescriptionItem name="Usage" 
                        :value="`${state.meta.layout.usage}%`"/>
                    <DescriptionItem name="Wastage" 
                        :value="`${state.meta.layout.wastage}%`"/>
                </div>
            </DescriptionList>
        </Section>
    </Modal>
</template>

<script>
import Modal from '@/components/Modal.vue';
import Section from '@/components/Section.vue';
import InputText from '@/components/InputText.vue';
import InputSelect from '@/components/InputSelect.vue';
import DescriptionList from '@/components/DescriptionList.vue';
import DescriptionItem from '@/components/DescriptionItem.vue';
import ChildSheetLayout from './ChildSheetLayout.vue';

import {reactive, computed, watch} from 'vue';
import {ChildSheetApi, SheetFedPressMachineApi} from '@/utils/apis.js';

export default {
    components: {
        Modal, Section, InputText, InputSelect, 
        DescriptionList, DescriptionItem, ChildSheetLayout
    },
    props: {
        isOpen: Boolean,
        childSheetId: Number,
        machineId: String,
        onAfterSave: Function
    },
    emits: ['toggle'],
    setup(props, {emit}) {
        const state = reactive({
            id: computed(()=>props.childSheetId),
            machineId: computed(()=>props.machineId),
            isCreate: computed(()=> state.id == null),
            isProcessing: false,
            error: '',
            data: {
                label: '', parent: null,
                width: 0, length: 0, 
                marginTop: 0, marginRight: 0, 
                marginBottom: 0, marginLeft: 0
            },
            meta: {
                parentSheet: computed(()=> 
                    state.meta.parentSheets.find(x=>x.id == state.data.parent)),
                parentSheets: [],
                parentPackSize: computed(()=> (state.meta.parentSheet)? 
                    state.meta.parentSheet.packSize : ''),
                uom: computed(()=> (state.meta.parentSheet)? state.meta.parentSheet.uom : ''),
                sizeValid: computed(()=> state.data.length != '' && state.data.width != ''),
                sizeRestrictions: computed(()=> {
                    const parentSheetLength = (state.meta.parentSheet)? 
                        state.meta.parentSheet.packLength : 0;
                    const parentSheetWidth = (state.meta.parentSheet)? 
                        state.meta.parentSheet.packWidth : 0;
                    const parentChildLengthDiff = parentSheetLength - state.data.length;
                    const parentChildWidthDiff = parentSheetWidth - state.data.width;
                    return {
                        maxLength: parentSheetLength,
                        maxWidth: parentSheetWidth,
                        maxMarginTop: (parentChildLengthDiff > state.data.marginBottom)? 
                            parentChildLengthDiff - state.data.marginBottom : 0,
                        maxMarginRight: (parentChildWidthDiff > state.data.marginRight)? 
                            parentChildWidthDiff - state.data.marginRight : 0,
                        maxMarginBottom: (parentSheetLength > state.data.marginTop)? 
                            parentChildLengthDiff - state.data.marginTop : 0,
                        maxMarginLeft: (parentChildWidthDiff > state.data.marginRight)? 
                            parentChildWidthDiff - state.data.marginRight : 0,
                    }
                }),
                layout: null,
                layoutRotate: true    
            },
            clearData: ()=> {
                state.data = {
                    label: '', parent: null, 
                    width: 0, length: 0, uom: '',
                    marginTop: 0, marginRight: 0, 
                    marginBottom: 0, marginLeft: 0};
            },
            clearMarginData: ()=> {
                state.data.marginTop = 0;
                state.data.marginBottom = 0;
                state.data.marginLeft = 0;
                state.data.marginRight = 0;
            },
            validate: ()=> {
                let errors = [];
                if (state.data.width == '' || state.data.width <= 0) errors.push('width');
                if (state.data.length == '' || state.data.length <= 0) errors.push('length');
                if (errors.length > 0)
                    state.error = `The following fields must not be empty and non-zero: ${errors.join(', ')}.`;
                else state.error = '';
                return errors.length > 0;
            },
            save: ()=> {
                if (state.validate()) return;
                const request = {
                    label: state.data.label,
                    parent: state.data.parent,
                    width_value: state.data.width,
                    length_value: state.data.length,
                    size_uom: state.meta.uom,
                    margin_top: state.data.marginTop,
                    margin_right: state.data.marginRight,
                    margin_bottom: state.data.marginBottom,
                    margin_left: state.data.marginLeft
                }
                saveChildSheet(request);
            }
        })

        const retrieveChildSheet = async (id) => {
            state.isProcessing = true;
            if (id) {
                const response = await ChildSheetApi.retrieveChildSheet(id);
                if (response) {
                    state.data = {
                        label: response.label, 
                        parent: response.parent,
                        width: response.width_value, 
                        length: response.length_value, 
                        uom: response.size_uom,
                        marginTop: response.margin_top, 
                        marginRight: response.margin_right, 
                        marginBottom: response.margin_bottom, 
                        marginLeft: response.margin_left
                    }
                }
            }
            state.isProcessing = false;
        }

        const saveChildSheet = async (sheet) => {
            state.isProcessing = true;
            let response = null;
            if (state.isCreate) {
                response = await SheetFedPressMachineApi.createSheetFedPressMachineChildSheet(
                    state.machineId, sheet);
            } else {
                response = await ChildSheetApi.updateChildSheet(state.id, sheet);
            }
            if (response) {
                if (props.onAfterSave) props.onAfterSave();
                emit('toggle', false)
            }
            state.isProcessing = false;
        }

        const retrieveParentSheets = async (id)=> {
            state.isProcessing = true;
            if (props.machineId) {
                const response = await SheetFedPressMachineApi.retrieveSheetFedPressMachineParentSheets(id);
                if (response) {
                    state.meta.parentSheets = response.map(obj=> ({
                        id: obj.id,
                        uom: obj.size_uom,
                        width: obj.width_value,
                        length: obj.length_value,
                        packWidth: obj.pack_width,
                        packLength: obj.pack_length,
                        paddingTop: obj.padding_top,
                        paddingRight: obj.padding_right,
                        paddingBottom: obj.padding_bottom,
                        paddingLeft: obj.padding_left,
                        size: obj.size,
                        packSize: obj.pack_size,
                        label: obj.label?
                            `${obj.label} (${obj.size})`: obj.size
                    }));
                }
            }
            state.isProcessing = false;
        }

        watch(()=> [props.isOpen], async ()=> {
            state.clearData()
            if (props.isOpen) {
                await retrieveParentSheets(state.machineId);
                if (!state.isCreate) {
                    await retrieveChildSheet(state.id);
                }
                state.error = '';
            }
        })

        return {
            state, 
        }
    }
}
</script>