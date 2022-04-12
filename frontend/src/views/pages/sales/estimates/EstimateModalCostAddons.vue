<template>
    <div class="grid grid-cols-3 gap-4">
        <div class="col-span-1">
            <InputSelect name="Template"
                @input="value => state.data.template = value"
                :options="state.meta.costAddonTemplates.map(c=>({
                    value: c.id, label: c.name,
                    isSelected: state.data.template == c.id
                }))"/>
        </div>
        <div v-if="state.meta.selectedTemplate" class="col-span-1">
            <InputSelect v-for="(item, key) in 
                    state.meta.selectedTemplate.templateCostAddonItems"
                :key="`${item.configCostAddon.name}-${key}`" 
                :name="item.configCostAddon.name" 
                :postfix="item.configCostAddon.symbol"
                :required="item.configCostAddon.isRequired"
                :customizable="item.configCostAddon.allowCustomValue"
                @input="value => {
                    state.data.costAddons[key].value = value;
                    emitInput();}"
                :regex="/^\d+\.?\d{0,2}/"
                :options="item.configCostAddon.options.map(c=>({
                    value: c.value,
                    description: c.label,
                    isSelected: state.data.costAddons[key].value == c.value
                }))"/>
        </div>
    </div>    
</template>
<script>
import InputSelect from '@/components/InputSelect.vue';
import {CostAddonApi} from '@/utils/apis.js';
import {reactive, watch, computed, onBeforeMount} from 'vue';

export default {
    components: {
        InputSelect
    },
    emits: ['input'],
    setup(_props, {emit}) {
        const state = reactive({
            data: {
                template: null,
                costAddons: []
            },
            meta: {
                costAddonTemplates: [],
                selectedTemplate: computed(()=>{
                    if (state.data.template)
                        return state.meta.costAddonTemplates.find(x =>
                            x.id == state.data.template)
                    else return null;
                })
            }
        });

        const listCostAddonTemplates = async () => {
            const response = await CostAddonApi.listTemplateCostAddons();
            state.meta.costAddonTemplates = response.map(x=>({
                id: x.id, name: x.name,
                isDefault: x.is_default,
                templateCostAddonItems: x.template_cost_addon_items.map(y=>({
                    id: y.id, sequence: y.sequence,
                    configCostAddon: {
                        id: y.config_cost_addon.id,
                        name: y.config_cost_addon.name,
                        type: y.config_cost_addon.type,
                        symbol: y.config_cost_addon.symbol,
                        allowCustomValue: y.config_cost_addon.allow_custom_value,
                        isRequired: y.config_cost_addon.is_required,
                        options: y.config_cost_addon.config_cost_addon_options.map(z=>({
                            id: z.id, label: z.label,
                            value: z.value, formattedValue: z.formatted_value
                        }))
                    }
                }))
            }));
        };

        onBeforeMount(async ()=> {
            await listCostAddonTemplates();
            const defaultTemplate = state.meta.costAddonTemplates.find(x => x.isDefault);
            if (defaultTemplate) state.data.template = defaultTemplate.id
        });

        watch(()=>state.meta.selectedTemplate, ()=> {
            if (state.meta.selectedTemplate) {
                state.data.costAddons = state.meta.selectedTemplate
                    .templateCostAddonItems.map(x => ({
                        sequence: x.sequence,
                        name: x.configCostAddon.name,
                        type: x.configCostAddon.type,
                        allow_custom_value: x.configCostAddon.allowCustomValue,
                        config_cost_addon: x.configCostAddon.id,
                        value: null
                    }));
            }
        });

        const emitInput = () => {
            console.log(state.data.costAddons)
            emit('input', state.data.costAddons);
        }

        return {
            state, emitInput
        }
    },
}
</script>
