<template>
    <Modal :heading="`${state.isCreate ? 'Add' : 'Edit'} Cost Add-on`" 
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
                <InputSelect name="Type" required 
                    @input="(value)=>state.data.type = value"
                    :options="state.meta.types.map(c=>({
                        value: c.value, label: c.display_name,
                        isSelected: state.data.type == c.value
                    }))"/>
            </div>
        </Section>
        <hr/>
        <Section heading="Add-on Options" heading-position="side">
            <InputCheckbox label="Is Required?" 
                :value="state.data.isRequired"
                @input="value => state.data.isRequired = value"/>
            <InputCheckbox label="Allow Custom Value?" 
                :value="state.data.allowCustomValue"
                @input="value => state.data.allowCustomValue = value"/>
            <ConfigCostAddonOptionListForm :type="state.data.type"
                @input="value => state.data.configCostAddonOptions = value"
                :value="state.data.configCostAddonOptions"/>
        </Section>
    </Modal>
</template>

<script>
import Modal from '@/components/Modal.vue';
import Section from '@/components/Section.vue';
import InputText from '@/components/InputText.vue';
import InputSelect from '@/components/InputSelect.vue';
import InputCheckbox from '@/components/InputCheckbox.vue';
import ConfigCostAddonOptionListForm from './ConfigCostAddonOptionListForm.vue';

import {reactive, computed, watch, onBeforeMount} from 'vue';
import {CostAddonApi} from '@/utils/apis.js';

export default {
    components: {
        Modal, Section, InputText, InputSelect, InputCheckbox, ConfigCostAddonOptionListForm
    },
    props: {
        isOpen: Boolean,
        configCostAddonId: Number
    },
    emits: ['toggle', 'saved'],
    setup(props, {emit}) {
        const state = reactive({
            id: computed(()=>props.configCostAddonId),
            isCreate: computed(()=> state.id == null),
            isProcessing: false,
            error: '',
            data: {
                name: '', type: '',
                allowCustomValue: false,
                isRequired: false,
                configCostAddonOptions: []
            },
            meta: {
                types: []
            },
            validate: ()=> {
                let errors = [];
                if (state.data.name == '' || state.data.name == null) errors.push('name');
                if (state.data.type == '' || state.data.type == null) errors.push('type');
                if (!state.data.allowCustomValue && state.data.configCostAddonOptions.length == 0)
                    errors.push('config cost add-on options')
                if (errors.length > 0)
                    state.error = `The following fields must not be empty: ${errors.join(', ')}.`;
                else state.error = '';
                return errors.length > 0;
            },
            save: ()=> {
                if (state.validate()) return;
                const configCostAddon = {
                    name: state.data.name, 
                    type: state.data.type,
                    is_required: state.data.isRequired,
                    allow_custom_value: state.data.allowCustomValue,
                    config_cost_addon_options: state.data
                        .configCostAddonOptions.map(x=> ({
                            id: x.id, label: x.label,
                            value: x.value
                        }))
                };
                saveConfigCostAddon(configCostAddon);
            },
            clear: ()=> {
                state.data = {
                    name: '', type: '',
                    allowCustomValue: false,
                    isRequired: false,
                    configCostAddonOptions: []
                }
            }
        });

        const getConfigCostAddonMeta = async () => {
            const response = await CostAddonApi.listConfigCostAddons(true);
            state.meta.types = response.actions.POST.type.choices;
        }

        const retrieveConfigCostAddon = async (id)=> {
            state.isProcessing = true;
            const response = await CostAddonApi.retrieveConfigCostAddon(id);
            if (response) {
                state.data = {
                    name: response.name, type: response.type,
                    isRequired: response.is_required,
                    allowCustomValue: response.allow_custom_value,
                    configCostAddonOptions: response.config_cost_addon_options
                };
            }
            state.isProcessing = false;
        }

        const saveConfigCostAddon = async (configCostAddon)=> {
            state.isProcessing = true;
            if (configCostAddon) {
                let response = null;
                if (!state.isCreate && state.id) {
                    response = await CostAddonApi.updateConfigCostAddon(state.id, configCostAddon);
                } else {
                    response = await CostAddonApi.createConfigCostAddon(configCostAddon);
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
                retrieveConfigCostAddon(id);
            } 
            if (!props.isOpen) state.clear()
        });

        onBeforeMount(getConfigCostAddonMeta);

        return {
            state
        }
    }
}
</script>