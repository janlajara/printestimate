<template>
    <Modal :heading="`${state.isCreate ? 'Add' : 'Edit'} Add-ons Template`" 
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
                <InputCheckbox label="Is default?" 
                    :value="state.data.is_default"
                    @input="value => state.data.is_default = value"/>
            </div>
        </Section>
        <hr/>
        <Section heading="Cost Add-ons" heading-position="side">
            <InputSelectDraggableList
                name="Add-on Options" :clone="false" required 
                class="flex-grow md:col-span-4"
                @input="(value)=> state.addonDragList.setValue(value)"
                :options="state.meta.addons.map(
                    c=>({value: c.id, label: c.name}))"
                :value="state.addonDragList.value"/>
        </Section>
    </Modal>
</template>

<script>
import Modal from '@/components/Modal.vue';
import Section from '@/components/Section.vue';
import InputText from '@/components/InputText.vue';
import InputCheckbox from '@/components/InputCheckbox.vue';
import InputSelectDraggableList from '@/components/InputSelectDraggableList.vue';

import {reactive, computed, watch, onBeforeMount} from 'vue';
import {CostAddonApi} from '@/utils/apis.js';

export default {
    components: {
        Modal, Section, InputText, InputCheckbox, InputSelectDraggableList
    },
    props: {
        isOpen: Boolean,
        templateCostAddonId: Number
    },
    emits: ['toggle', 'saved'],
    setup(props, {emit}) {
        const state = reactive({
            id: computed(()=>props.templateCostAddonId),
            isCreate: computed(()=> state.id == null),
            isProcessing: false,
            error: '',
            data: {
                name: '', 
                is_default: false,
                template_cost_addon_items: []
            },
            meta: {
                addons: []
            },
            addonDragList: {
                value: computed(()=> 
                    state.data.template_cost_addon_items
                        .map(x => x.config_cost_addon.id)),
                setValue: (value) => {
                    let addonItems = [];
                    value.forEach(x => {
                        let addonItem = state.data.template_cost_addon_items
                            .find(y => y.config_cost_addon.id == x);
                        if (addonItem == null) 
                            addonItem = {config_cost_addon: {id: x}} 
                        addonItems.push(addonItem)
                    });
                    state.data.template_cost_addon_items = addonItems;
                }
            },
            validate: ()=> {
                let errors = [];
                if (state.data.name == '' || state.data.name == null) errors.push('name');
                if (state.data.template_cost_addon_items.length == 0)
                    errors.push('template cost add-on options')
                if (errors.length > 0)
                    state.error = `The following fields must not be empty: ${errors.join(', ')}.`;
                else state.error = '';
                return errors.length > 0;
            },
            save: ()=> {
                if (state.validate()) return;
                const templateCostAddon = {
                    name: state.data.name, 
                    is_default: state.data.is_default,
                    template_cost_addon_items: state.data
                        .template_cost_addon_items.map(x=> ({
                            id: x.id, 
                            config_cost_addon: x.config_cost_addon.id
                        }))
                };
                saveTemplateCostAddon(templateCostAddon);
            },
            clear: ()=> {
                state.data = {
                    name: '', 
                    is_default: false,
                    template_cost_addon_items: []
                }
            }
        });

        const listConfigCostAddons = async () => {
            const response = await CostAddonApi.listConfigCostAddons();
            state.meta.addons = response.map(x => ({
                id: x.id, name: x.name}));
        }

        const retrieveTemplateCostAddon = async (id)=> {
            state.isProcessing = true;
            const response = await CostAddonApi.retrieveTemplateCostAddon(id);
            if (response) {
                state.data = {
                    name: response.name, is_default: response.is_default,
                    template_cost_addon_items: response.template_cost_addon_items
                        .map(x => ({
                            id: x.id, sequence: x.sequence,
                            config_cost_addon: {
                                id: x.config_cost_addon.id,
                                name: x.config_cost_addon.name
                            }
                        }))
                };
            }
            state.isProcessing = false;
        }

        const saveTemplateCostAddon = async (templateCostAddon)=> {
            state.isProcessing = true;
            if (templateCostAddon) {
                let response = null;
                if (!state.isCreate && state.id) {
                    response = await CostAddonApi.updateTemplateCostAddon(state.id, templateCostAddon);
                } else {
                    response = await CostAddonApi.createTemplateCostAddon(templateCostAddon);
                }
                if (response) {
                    emit('saved');
                    emit('toggle', false);
                }
            }
            state.isProcessing = false;
        }

        watch(()=> props.isOpen, ()=> { 
            if (props.isOpen && state.id && !state.isCreate) {
                const id = parseInt(state.id);
                retrieveTemplateCostAddon(id);
            } 
            if (!props.isOpen) state.clear()
        });

        onBeforeMount(listConfigCostAddons);

        return {
            state
        }
    }
}
</script>