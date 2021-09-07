<template>
    <Section heading="Components" heading-position="side"> 
        <div class="md:grid md:gap-4 md:grid-cols-3">
            <div v-for="(component, key) in state.meta.components" :key="key">
                <span>{{component.name}}</span>
                <span class="capitalize">{{component.type}}</span>
                <InputSelect name="Material" required 
                    class="flex-grow md:col-span-2"
                    :multiple="component.allowMultipleMaterials"
                    v-if="component.metaMaterialOptions.length > 0"
                    @input="()=>{}"
                    :options="component.metaMaterialOptions.map(c=>({
                        value: c.id, label: c.label
                    }))"/>
                <InputSelect name="Machine" required 
                    v-if="component.metaMachineOptions.length > 0"
                    @input="()=>{}"
                    :options="component.metaMachineOptions.map(c=>({
                        value: c.id, label: c.label
                    }))"/>
            </div>
        </div>
    </Section>
</template>
<script>
import Section from '@/components/Section.vue';
import InputSelect from '@/components/InputSelect.vue';

import {reactive, watch, computed, onBeforeMount} from 'vue';
import {MetaProductApi, ComponentTemplateApi} from '@/utils/apis.js';

export default {
    props: {
        metaProductId: [Number, String]
    },
    components: {
        Section, InputSelect
    },
    setup(props) {
        const state = reactive({
            id: computed(()=> props.metaProductId),
            data: {
                componentTemplates: []
            },
            meta: {
                components: [],
                componentFields: [],
            }
        })

        const retrieveMetaProductComponents = async (id) => {
            state.isProcessing = true;
            if (id) {
                const response = await MetaProductApi.retrieveMetaProductComponents(id);
                if (response) {
                    state.meta.components = response.map(obj=> ({
                        id: obj.id,
                        name: obj.name,
                        type: obj.type,
                        allowMultipleMaterials: obj.allow_multiple_materials,
                        metaEstimateVariables: obj.meta_estimate_variables,
                        metaMaterialOptions: obj.meta_material_options,
                        metaMachineOptions: obj.meta_machine_options
                    }));
                }
            }
            state.isProcessing = false;
        }
        
        const getComponentTemplateFields = async () => {
            const response = await ComponentTemplateApi.getComponentMetaData();
            if (response) {
                console.log(response.data)
                state.meta.componentFields = response.data
                    .map(obj => ({
                        type: obj.type, 
                        fields: obj.fields
                    }))
            }
            console.log(state.meta.componentFields);
        }

        onBeforeMount(getComponentTemplateFields);
        watch(()=> state.id, ()=> {console.log(state.id)
            if (state.id) {
                retrieveMetaProductComponents(state.id);
            }
        })

        return {
            state
        }
    }
}
</script>