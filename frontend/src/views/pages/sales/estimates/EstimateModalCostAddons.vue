<template>
    <div class="grid lg:grid-cols-3 lg:gap-4">
        <div class="col-span-1" v-if="!state.data.isValueProvided">
            <InputSelect 
                name="Template"
                @input="value => {
                    state.data.template = value;
                    initializeCostAddons();}"
                :options="state.meta.costAddonTemplates.map(c=>({
                    value: c.id, label: c.name,
                    isSelected: state.data.template == c.id
                }))"/>
        </div>
        <div v-if="state.meta.selectedTemplateAddonItems" 
            class="col-span-1">
            <InputSelect v-for="(item, key) in 
                    state.meta.selectedTemplateAddonItems"
                :key="`k-${key}${new Date().getTime()}`" 
                :name="item.name" 
                :postfix="item.symbol"
                :required="item.is_required"
                :customizable="item.allow_custom_value"
                @input="value => {
                    state.data.costAddons[key].value = value;
                    emitInput();}"
                :regex="/^\d+\.?\d{0,2}/"
                :options="item.options"/>
        </div>
    </div>    
</template>
<script>
import InputSelect from '@/components/InputSelect.vue';
import {CostAddonApi} from '@/utils/apis.js';
import {reactive, computed, onBeforeMount} from 'vue';

export default {
    components: {
        InputSelect
    },
    props: {
        value: Object
    },
    emits: ['input'],
    setup(props, {emit}) {
        const state = reactive({
            data: {
                isValueProvided: computed(()=> (
                    state.data.value && state.data.value.id != null && 
                    state.data.value.estimateAddonItems.length > 0)),
                value: computed(()=> props.value),
                template: null,
                costAddons: []
            },
            meta: {
                costAddonConfigs: [],
                costAddonTemplates: [],
                selectedTemplateAddonItems: computed(()=> {
                    const initialized = initializeCostAddons();
                    state.data.costAddons = initialized.costAddons;
                    return initialized.selectedTemplateAddonItems;
                })
            }
        });

        const listCostAddonConfigs = async () => { 
            const response = await CostAddonApi.listConfigCostAddons();
            state.meta.costAddonConfigs = response.map(x => ({
                id: x.id, name: x.name, symbol: x.symbol,
                type: x.type, options: x.config_cost_addon_options
            }));
        }

        const listCostAddonTemplates = async () => {
            const response = await CostAddonApi.listTemplateCostAddons();
            state.meta.costAddonTemplates = response.map(x=>({
                id: x.id, name: x.name,
                isDefault: x.is_default,
                templateCostAddonItems: x.template_cost_addon_items.map(y=>({
                    id: y.id, 
                    sequence: y.sequence,
                    name: y.config_cost_addon.name,
                    type: y.config_cost_addon.type,
                    symbol: y.config_cost_addon.symbol,
                    allow_custom_value: y.config_cost_addon.allow_custom_value,
                    config_cost_addon: y.config_cost_addon.id,
                    is_required: y.config_cost_addon.is_required,
                    options: y.config_cost_addon.config_cost_addon_options.map(z=>({
                        id: z.id, label: z.label,
                        value: z.value, formattedValue: z.formatted_value
                    }))
                        
                }))
            }));
        };

        const initializeCostAddons = ()=> {
            let selectedTemplateAddonItems = [];
            let costAddons = [];
            
            if (state.meta.costAddonTemplates.length > 0 && 
                    state.meta.costAddonConfigs.length > 0) {

                if (!state.data.isValueProvided) {
                    const template = state.meta.costAddonTemplates.find(x =>
                        x.id == state.data.template);
                    let templateAddonItems = template.templateCostAddonItems;
                    templateAddonItems.forEach(x => {
                        x.options = x.options.map(x => ({
                            value: x.value,
                            description: x.label,
                            isSelected: false 
                        }));
                    });
                    selectedTemplateAddonItems = templateAddonItems;

                    const defaultCostAddons = selectedTemplateAddonItems.map(x => ({
                            sequence: x.sequence,
                            name: x.name,
                            type: x.type,
                            allow_custom_value: x.allow_custom_value,
                            config_cost_addon: x.config_cost_addon,
                            value: null
                        }));
                    costAddons =  defaultCostAddons;

                } else {
                    costAddons = props.value.estimateAddonItems;
                    selectedTemplateAddonItems = costAddons.map(x => {
                        let match = state.meta.costAddonConfigs.find(y => 
                            y.id == x.config_cost_addon);
                        const optionsHasMatch = match.options
                            .findIndex(z => z.value == x.value) >= 0;
                        if (!optionsHasMatch) {
                            match.options.push({
                                value: x.value,
                                label: 'Custom',
                                isSelected: true
                            });
                        }
                        return {
                            ...x,
                            symbol: match.symbol,
                            is_required: match.is_required,
                            options: match.options.map(z => ({
                                value: z.value,
                                description: z.label,
                                isSelected: x.value == z.value
                            }))
                        }
                    });
                }
            }

            return {selectedTemplateAddonItems, costAddons}
        };

        onBeforeMount(async ()=> {
            await listCostAddonConfigs();
            await listCostAddonTemplates();
            const defaultTemplate = state.meta.costAddonTemplates.find(x => x.isDefault);
            if (defaultTemplate) {
                state.data.template = defaultTemplate.id;
                const initialized = initializeCostAddons();
                state.data.costAddons = initialized.costAddons;
            }
        });
        
        const emitInput = () => {
            emit('input', state.data.costAddons);
        }

        return {
            state, emitInput, initializeCostAddons
        }
    },
}
</script>
