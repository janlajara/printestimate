 <template>
    <Modal :heading="`${state.isCreate ? 'Add' : 'Edit'} Component`" 
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
                <InputSelect name="Material Type" required 
                    :disabled="state.data.metaProperties.length > 0"
                    @input="(value)=>state.data.type = value"
                    :options="state.meta.materialTypeChoices.map(c=>({
                        value: c.value, label: c.label,
                        isSelected: state.data.type == c.value
                    }))"/>
            </div>
        </Section>
        <hr/>
        <Section heading="Materials" heading-position="side"> 
            <div class="md:grid md:gap-4 md:grid-cols-3">
            </div>
        </Section>
        <hr/>
        <Section heading="Properties" heading-position="side"> 
            <MetaComponentPropertiesListForm 
                :material-type="state.data.type"
                :option-type-choices="state.meta.optionTypeChoices"
                :value="state.data.metaProperties"
                @input="value => state.data.metaProperties = value"/>
        </Section>
    </Modal>
</template>

<script>
import Modal from '@/components/Modal.vue';
import Section from '@/components/Section.vue';
import InputText from '@/components/InputText.vue';
import InputSelect from '@/components/InputSelect.vue';
import MetaComponentPropertiesListForm from './MetaComponentPropertiesListForm.vue'

import {reactive, computed, watch, onBeforeMount} from 'vue';
import {MetaProductApi, MetaComponentApi} from '@/utils/apis.js';

export default {
    components: {
        Modal, Section, InputText, InputSelect,
        MetaComponentPropertiesListForm
    },
    props: {
        isOpen: Boolean,
        metaComponentId: Number,
        metaProductId: Number,
        onAfterSave: Function
    },
    emits: ['toggle'],
    setup(props, {emit}) { 
        const state = reactive({
            id: computed(()=>props.metaComponentId),
            metaProductId: computed(()=>props.metaProductId),
            isCreate: computed(()=> state.id == null),
            isProcessing: false,
            error: '',
            data: {
                name: '', 
                type: '', 
                metaProperties: [],
                metaMaterialOptions: []
            },
            meta: {
                materialTypeChoices: [],
                optionTypeChoices: []
            },
            clearData: ()=> {
                state.data = {
                    name: '', 
                    type: '', 
                    metaProperties: [],
                    metaMaterialOptions: []
                }
            },
            validate: ()=> {
                let errors = [];
                if (state.data.name == '') 
                    errors.push('name');
                if (state.data.type == '') 
                    errors.push('type');
                if (errors.length > 0)
                    state.error = `The following fields must not be empty: ${errors.join(', ')}.`;
                else state.error = '';
                return errors.length > 0;
            },
            save: ()=> {
                if (state.validate()) return;
                const request = {
                    name: state.data.name,
                    type: state.data.type,
                    meta_material_options: state.data.metaMaterialOptions.map( y => ({
                        id: y.id,
                        label: y.label,
                        item: y.item
                    })),
                    meta_properties: state.data.metaProperties.map( x => ({
                        id: x.id,
                        name: x.name,
                        costing_measure: x.costingMeasure,
                        options_type: x.optionsType,
                        is_required: x.isRequired,
                        meta_property_options: x.metaPropertyOptions.map( y => ({
                            operation: y.operation
                        }))
                    }))
                };
                saveComponent(request);
            }
        })

        const retrieveComponent = async (id) => {
            state.isProcessing = true;
            if (id) {
                const response = await MetaComponentApi.retrieveMetaComponent(id);
                if (response) {
                    state.data = {
                        name: response.name, 
                        type: response.type, 
                        metaProperties: response.meta_properties.map( x => ({
                            id: x.id,
                            name: x.name,
                            costingMeasure: x.costing_measure,
                            optionsType: x.options_type,
                            isRequired: x.is_required,
                            metaPropertyOptions: x.meta_property_options.map( y => ({
                                id: y.id,
                                label: y.label,
                                operation: y.operation
                            }))
                        })),
                        metaMaterialOptions: response.meta_material_options.map( z => ({
                            id: z.id,
                            label: z.label,
                            item: z.item
                        }))
                    }
                }
            }
            state.isProcessing = false;
        }

        const retrieveComponentMetaData = async (id) => {
            if (id) {
                const response = await MetaProductApi.retrieveMetaProductComponents(id, true);
                const metadata = response.actions.POST;
                state.meta = {
                    materialTypeChoices: metadata.type.choices.map( x => ({
                        value: x.value, label: x.display_name
                    })),
                    optionTypeChoices: metadata.meta_properties.child.children.options_type.choices.map( y => ({
                        value: y.value, label: y.display_name
                    })),
                }
            }
        }

        const saveComponent = async (component) => {
            state.isProcessing = true;
            let response = null;
            if (state.isCreate) {
                response = await MetaProductApi.createMetaProductComponent(
                    state.metaProductId, component);
            } else {
                response = await MetaComponentApi.updateMetaComponent(
                    state.id, component);
            }
            if (response) {
                if (props.onAfterSave) props.onAfterSave();
                emit('toggle', false);
            }
            state.isProcessing = false;
        }

        watch(()=> [props.isOpen], ()=> {
            if (props.isOpen) {
                if (!state.isCreate) retrieveComponent(state.id);
                else state.clearData();
                state.error = '';
            }
        })
        onBeforeMount(async ()=> {
            await retrieveComponentMetaData(state.metaProductId);
        })

        return {
            state
        }
    }
}
</script>