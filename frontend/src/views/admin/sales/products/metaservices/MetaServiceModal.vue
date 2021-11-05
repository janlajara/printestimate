 <template>
    <Modal :heading="`${state.isCreate ? 'Add' : 'Edit'} Service`" 
        :is-open="$props.isOpen" @toggle="(value)=> $emit('toggle', value)"
        :buttons="[{color: 'primary', icon:'save', text:'Save', 
            action: state.save, disabled: state.isProcessing},]">
        <div v-if="state.error" 
            class="pt-4 text-sm text-red-600">*{{state.error}}</div>
        <Section heading="General Information" heading-position="side"> 
            <div class="md:grid md:gap-4 md:grid-cols-3">
                <InputText name="Name"  placeholder="Name"
                    type="text" :value="state.data.name" required
                    @input="value => state.data.name = value"/>
                <InputSelect :disabled="state.data.metaOperations.length > 0"
                    name="Material Type" required 
                    @input="(value)=> {
                        state.data.type = value;
                        state.costingMeasure = '';
                        state.data.component = '';
                    }"
                    :options="state.meta.materialTypeChoices.map(c=>({
                        value: c.value, label: c.label,
                        isSelected: state.data.type == c.value
                    }))"/>
                <InputSelect :disabled="state.data.metaOperations.length > 0"
                    name="Costing Measure" required 
                    @input="(value)=>state.data.costingMeasure = value"
                    :options="state.meta.costingMeasureChoices.map(c=>({
                        value: c.value, label: c.label,
                        isSelected: state.data.costingMeasure == c.value
                    }))"/>
            </div>
        </Section>
        <hr/>
        <Section heading="Input" heading-position="side"> 
            <div class="md:grid md:gap-4 md:grid-cols-3">
                <InputSelect 
                    name="Component" 
                    @input="(value)=>state.data.component = value"
                    :options="state.meta.metaComponentChoices.map(c=>({
                        value: c.value, label: c.label,
                        isSelected: state.data.component == c.value
                    }))"/>
                <InputSelect :required="state.data.component == true"
                    :name="`${state.data.costingMeasure} Derived From`" 
                        class="col-span-2 capitalize"
                    @input="(value)=>state.data.estimateVariableType = value"
                    :options="state.meta.estimateVariableTypeChoices.map(c=>({
                        value: c.value, label: c.label,
                        isSelected: state.data.estimateVariableType == c.value
                    }))"/>
            </div>
        </Section>
        <hr/>
        <Section heading="Operations" heading-position="side"> 
            <MetaServiceOperationsListForm 
                :material-type="state.data.type"
                :costing-measure="state.data.costingMeasure"
                :option-type-choices="state.meta.optionTypeChoices"
                :value="state.data.metaOperations"
                @input="value => state.data.metaOperations = value"/>
        </Section>
    </Modal>
</template>

<script>
import Modal from '@/components/Modal.vue';
import Section from '@/components/Section.vue';
import InputText from '@/components/InputText.vue';
import InputSelect from '@/components/InputSelect.vue';
import MetaServiceOperationsListForm from './MetaServiceOperationsListForm.vue';

import {reactive, computed, watch, onBeforeMount} from 'vue';
import {MetaProductApi, MetaServiceApi, OperationApi} from '@/utils/apis.js';

export default {
    components: {
        Modal, Section, InputText, InputSelect,
        MetaServiceOperationsListForm
    },
    props: {
        isOpen: Boolean,
        metaServiceId: Number,
        metaProductId: Number,
        metaComponentList: Array,
        onAfterSave: Function
    },
    emits: ['toggle'],
    setup(props, {emit}) { 
        const state = reactive({
            id: computed(()=>props.metaServiceId),
            metaProductId: computed(()=>props.metaProductId),
            isCreate: computed(()=> state.id == null),
            isProcessing: false,
            error: '',
            data: {
                name: '', 
                type: '', 
                costingMeasure: '',
                component: '',
                estimateVariableType: '',
                metaOperations: [],
            },
            meta: {
                optionTypeChoices: [],
                materialTypeChoices: [],
                costingMeasureChoicesMapping: [],
                costingMeasureChoices: computed(()=> {
                    const mapping =  state.meta.costingMeasureChoicesMapping.filter(
                        c => c.key == state.data.type);
                    if (mapping && mapping[0]) {
                        return mapping[0].value.map(c=> ({
                            value: c.value, label: c.display
                        }));
                    } else return [];
                }),
                metaComponents: computed(()=> props.metaComponentList),
                metaComponentChoices: computed(()=> 
                    props.metaComponentList
                        .filter(x => x.type == state.data.type)
                        .map(x => ({
                        value: x.id, label: x.name
                    }))),
                estimateVariableTypes: computed(()=> {
                    const component = state.meta.metaComponents.find(
                        x => x.id == state.data.component);
                    let filteredTypes = [];
                    if (component) {                        
                        filteredTypes = component.metaEstimateVariables.filter(
                            x => x.costing_measure == state.data.costingMeasure
                        );
                    }
                    return filteredTypes
                }),
                estimateVariableTypeChoices: computed(()=> 
                    state.meta.estimateVariableTypes.map(x => ({
                        value: x.type, label: x.label
                })))
            },
            clearData: ()=> {
                state.data = {
                    name: '', 
                    type: '', 
                    costingMeasure: '',
                    component: '',
                    estimateVariableType: '',
                    metaOperations: [],
                }
            },
            validate: ()=> {
                let errors = [];
                if (state.data.name == '') errors.push('name');
                if (state.data.type == '') errors.push('type');
                if (state.data.costingMeasure == '') errors.push('costing measure');
                if (state.data.component != '' &&
                    state.data.estimateVariableType == '') errors.push('derived from');
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
                    costing_measure: state.data.costingMeasure,
                    meta_component: state.data.component,
                    estimate_variable_type: state.data.estimateVariableType,
                    meta_operations: state.data.metaOperations.map( x => ({
                        id: x.id,
                        name: x.name,
                        options_type: x.optionsType,
                        is_required: x.isRequired,
                        meta_operation_options: x.metaOperationOptions.map( y => ({
                            id: y.id,
                            operation: y.operation
                        }))
                    }))
                };
                saveService(request);
            }
        })

        const retrieveService = async (id) => {
            state.isProcessing = true;
            if (id) {
                const response = await MetaServiceApi.retrieveMetaService(id);
                if (response) {
                    state.data = {
                        name: response.name, 
                        type: response.type, 
                        costingMeasure: response.costing_measure,
                        component: response.meta_component,
                        estimateVariableType: response.estimate_variable_type,
                        metaOperations: response.meta_operations.map( x => ({
                            id: x.id,
                            name: x.name,
                            optionsType: x.options_type,
                            isRequired: x.is_required,
                            metaOperationOptions: x.meta_operation_options.map( y => ({
                                id: y.id,
                                label: y.label,
                                operation: y.operation,
                                workstation: x.workstation,
                            }))
                        }))
                    }
                }
            }
            state.isProcessing = false;
        }

        const retrieveServiceMetaData = async (id) => {
            if (id) {
                const response = await MetaProductApi.retrieveMetaProductServices(id, true);
                const metadata = response.actions.POST;
                state.meta.materialTypeChoices = metadata.type.choices.map( x => ({
                    value: x.value, label: x.display_name
                }));
                state.meta.optionTypeChoices = metadata.meta_operations.child.children.options_type.choices.map( y => ({
                    value: y.value, label: y.display_name
                }));
            }
        }

        const listCostingMeasures = async () => {
            const response = await OperationApi.listOperationCostingMeasures();
            if (response) {
                state.meta.costingMeasureChoicesMapping = response.map(c=> ({
                    key: c.material, value:c.measure_choices
                }));
            }
        }

        const saveService = async (service) => {
            state.isProcessing = true;
            let response = null;
            if (state.isCreate) {
                response = await MetaProductApi.createMetaProductService(
                    state.metaProductId, service);
            } else {
                response = await MetaServiceApi.updateMetaService(
                    state.id, service);
            }
            if (response) {
                if (props.onAfterSave) props.onAfterSave();
                emit('toggle', false);
            }
            state.isProcessing = false;
        }

        watch(()=> [props.isOpen], ()=> {
            if (props.isOpen) {
                if (!state.isCreate) retrieveService(state.id);
                else state.clearData();
                state.error = '';
            }
        })
        onBeforeMount(async ()=> {
            await listCostingMeasures();
            await retrieveServiceMetaData(state.metaProductId);
        })

        return {
            state
        }
    }
}
</script>