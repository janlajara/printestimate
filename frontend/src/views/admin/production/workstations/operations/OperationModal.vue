<template>
    <Modal :heading="`${state.isCreate ? 'Add' : 'Edit'} Operation`" 
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
                <InputSelect name="Material Type" required :disabled="!state.isCreate"
                    @input="(value)=> {
                        state.data.materialType = value;
                        state.data.costingMeasure = '';
                    }"
                    :options="state.meta.materialTypeChoices.map(c=>({
                        value: c.value, label: c.label,
                        isSelected: state.data.materialType == c.value
                    }))"/>
                 <InputSelect name="Costing Measure" required :disabled="!state.isCreate"
                    @input="(value)=>state.data.costingMeasure = value"
                    :options="state.meta.costingMeasureChoices.map(c=>({
                        value: c.value, label: c.label,
                        isSelected: state.data.costingMeasure == c.value
                    }))"/>
            </div>
        </Section>
        <div v-if="!state.isCreate">
            <Section heading="Operaton Steps" heading-position="side"> 
                <Table :headers="['#', 'Activity', 'Notes', '']" 
                    :rows="state.data.operationSteps" :no-body="true">
                    <draggable v-model="state.data.operationSteps" tag="tbody" item-key="id"
                         class="bg-white divide-y divide-gray-200">
                        <template #item="{element}">
                            <Row>
                                <Cell>{{element.sequence}}</Cell>
                                <Cell>{{element.activity}} : {{element.rate}}</Cell>
                                <Cell>{{element.notes}}</Cell>
                                <Cell>
                                    <Button class="my-auto" icon="delete"
                                        @click="()=>{}"/>
                                </Cell>
                            </Row>
                        </template>
                    </draggable>
                 </Table>
                <div>
                    <InputTextLookup placeholder="Search Activity" class="flex-grow"
                        :value="state.data.add.activityLookupText"
                        @select="selected => state.data.add.activity = selected"
                        @input="value => state.data.add.activityLookupText = value"
                        :options="state.meta.activityChoices.map( option => ({
                            value: option.value,
                            title: option.title,
                            subtitle: option.subtitle,
                            figure: option.figure
                        }))"/>
                    <InputTextarea placeholder="Notes" 
                        :value="`${state.data.add.notes}`"
                        @input="value => state.data.add.notes = value"/>
                    <div class="flex justify-end mt-2">
                        <Button icon="add" class="my-auto"
                            @click="state.addOperationStep">Add</Button>
                    </div>
                </div>
            </Section>
        </div>
    </Modal>
</template>

<script>
import Modal from '@/components/Modal.vue';
import Section from '@/components/Section.vue';
import InputText from '@/components/InputText.vue';
import InputTextarea from '@/components/InputTextarea.vue';
import InputSelect from '@/components/InputSelect.vue';
import Table from '@/components/Table.vue';
import Row from '@/components/Row.vue'
import Cell from '@/components/Cell.vue'
import Button from '@/components/Button.vue';
import InputTextLookup from '@/components/InputTextLookup.vue';
import draggable from 'vuedraggable';

import {reactive, computed, watch, inject, onBeforeMount} from 'vue';
import {WorkstationApi, OperationApi} from '@/utils/apis.js';

export default {
    components: {
        Modal, Section, InputText, InputTextarea, InputSelect, 
        InputTextLookup, Table, Row, Cell, Button, draggable
    },
    props: {
        isOpen: Boolean,
        operationId: Number,
        workstationId: Number,
        onAfterSave: Function
    },
    emits: ['toggle'],
    setup(props, {emit}) { 
        const currency = inject('currency');
        const state = reactive({
            id: computed(()=>props.operationId),
            workstationId: computed(()=>props.workstationId),
            isCreate: computed(()=> state.id == null),
            isProcessing: false,
            error: '',
            data: {
                name: '', 
                materialType: '',
                costingMeasure: '',
                operationSteps: [],
                add: {
                    activity: '',
                    activityLookupText: '',
                    notes: ''
                }
            },
            meta: {
                materialTypeChoices: [],
                activityChoices: [],
                costingMeasureChoicesMapping: [],
                costingMeasureChoices: computed(()=> {
                    const mapping =  state.meta.costingMeasureChoicesMapping.filter(
                        c => c.key == state.data.materialType);
                    if (mapping && mapping[0]) {
                        return mapping[0].value.map(c=> ({
                            value: c.value, label: c.display
                        }));
                    } else return [];
                }),
            },
            clearData: ()=> {
                state.data = {
                    name: '', 
                    materialType: '',
                    costingMeasure: '',
                    operationSteps: [],
                    add: {
                        activity: '',
                        activityLookupText: '',
                        notes: ''
                    }
                }
            },
            validate: ()=> {
                let errors = [];
                if (state.data.name == '') errors.push('name');
                if (state.data.materialType == '') errors.push('material type');
                if (state.data.costingMeasure == '') errors.push('costing measure');
                if (errors.length > 0)
                    state.error = `The following fields must not be empty: ${errors.join(', ')}.`;
                else state.error = '';
                return errors.length > 0;
            },
            save: ()=> {
                if (state.validate()) return;
                const request = {
                    name: state.data.name,
                    material_type: state.data.materialType,
                    costing_measure: state.data.costingMeasure
                }
                saveOperation(request);
            },
            validateAddOperationStep: ()=> {
                let errors = [];
                if (state.data.add.activity == '') errors.push('activity');
                if (state.data.add.notes == '') errors.push('notes');
                if (errors.length > 0)
                    state.error = `The following fields must not be empty: ${errors.join(', ')}.`;
                else state.error = '';
                return errors.length > 0;
            },
            addOperationStep: async ()=> {
                if (state.validateAddOperationStep()) return;
                const request = {
                    activity: state.data.add.activity,
                    notes: state.data.add.notes
                }
                const response = await createOperationStep(state.id, request);
                if (response) retrieveOperationSteps(state.id)
            }
        })

        const retrieveOperation = async (id) => {
            state.isProcessing = true;
            if (id) {
                const response = await OperationApi.retrieveOperation(id);
                if (response) {
                    state.data.name = response.name; 
                    state.data.materialType = response.material_type;
                    state.data.costingMeasure = response.costing_measure;
                    state.meta.activityChoices = response.activity_choices.map(obj=> ({
                        value: obj.id,
                        title: obj.name,
                        subtitle: obj.speed.rate,
                        figure: obj.measure,
                    }));
                }
            }
            state.isProcessing = false;
        }

        const retrieveOperationMetaData = async (id) => {
            const response1 = await OperationApi.listOperationCostingMeasures();
            if (response1) {
                state.meta.costingMeasureChoicesMapping = response1.map(c=> ({
                    key: c.material, value:c.measure_choices
                }));
            }

            if (id) {
                const response2 = await WorkstationApi.retrieveWorkstationOperations(
                    id, true);
                state.meta.materialTypeChoices = 
                    response2.actions.POST.material_type.choices.map(c=> ({
                        value: c.value, label: c.display_name
                    }));
            }
        }

        const retrieveOperationSteps = async (id)=> {
            state.isProcessing = true;
            if (id) {
                const response = await OperationApi.retrieveOperationSteps(id);
                if (response) {
                    state.data.operationSteps = response.map(obj=> ({
                        id: obj.id, sequence: obj.sequence,
                        activity: obj.activity.name, rate: obj.activity.speed.rate,
                        notes: obj.notes
                    }));
                }
            }
            state.isProcessing = false;
        }

        const saveOperation = async (operation) => {
            state.isProcessing = true;
            let response = null;
            if (state.isCreate) {
                response = await WorkstationApi.createWorkstationOperation(
                    state.workstationId, operation);
            } else {
                response = await OperationApi.updateOperation(
                    state.id, operation);
            }
            if (response) {
                if (props.onAfterSave) props.onAfterSave();
                emit('toggle', false);
            }
            state.isProcessing = false;
        }

        const createOperationStep = async (id, operationStep)=> {
            state.isProcessing = true;
            if (id && operationStep) {
                const response = await OperationApi.createOperationStep(id, operationStep);
                state.isProcessing = false;
                return response;
            }
            state.isProcessing = false;
        }

        watch(()=> [props.isOpen], ()=> {
            if (props.isOpen) {
                state.clearData();
                if (!state.isCreate) {
                    retrieveOperation(state.id);
                    retrieveOperationSteps(state.id);
                } 
                state.error = '';
            }
        })
        onBeforeMount(()=> {
            retrieveOperationMetaData(state.workstationId);
        })

        return {
            state, currency
        }
    }
}
</script>