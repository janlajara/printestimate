<template>
    <Modal :heading="`${state.isCreate ? 'Add' : 'Edit'} Operation`" 
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
                    :disabled="state.data.operationSteps.length > 0"
                    @input="(value)=> {
                        state.data.materialType = value;
                        state.data.costingMeasure = '';
                        state.clearOperationStepForm();
                    }"
                    :options="state.meta.materialTypeChoices.map(c=>({
                        value: c.value, label: c.label,
                        isSelected: state.data.materialType == c.value
                    }))"/>
                 <InputSelect name="Costing Measure" required 
                    :disabled="state.data.operationSteps.length > 0"
                    @input="(value)=>{
                        state.data.costingMeasure = value;
                        state.data.measureUnit = '';
                        state.clearOperationStepForm();
                    }"
                    :options="state.meta.costingMeasureChoices.map(c=>({
                        value: c.value, label: c.label,
                        isSelected: state.data.costingMeasure == c.value
                    }))"/>
                <InputSelect name="Measure Unit" required 
                    :disabled="state.data.operationSteps.length > 0 || 
                        state.data.costingMeasure == ''"
                    @input="(value)=>{
                        state.data.measureUnit = value;
                        state.clearOperationStepForm();
                    }"
                    :options="state.meta.measureUnitChoices
                        .filter(x=> state.meta.costingMeasureChoice &&
                            x.measure == state.meta.costingMeasureChoice.base_measure)
                        .map(c=>({
                            value: c.value, label: c.label,
                            isSelected: state.data.measureUnit == c.value
                        }))"/>
            </div>
        </Section>
        <div>
            <Section heading="Operaton Steps" heading-position="side"> 
                <Table :headers="['Step #', 'Activity', 'Notes', '']" :no-body="true">
                    <draggable v-model="state.data.operationSteps" tag="tbody" 
                        item-key="id" handle=".drag" @change="state.updateOperationSteps"
                        class="bg-white divide-y divide-gray-200">
                        <template #item="{element}">
                            <Row class="drag cursor-move">
                                <Cell label="Step #">
                                    <div class="grid grid-cols-2 gap-x-2">
                                        <span class="material-icons text-xs my-auto">drag_indicator</span>
                                        <span>{{element.sequence}}</span>
                                    </div>
                                </Cell>
                                <Cell label="Activity">{{element.activityName}}</Cell>
                                <Cell label="Notes">{{element.notes}}</Cell>
                                <Cell>
                                    <Button class="my-auto" icon="clear" 
                                        @click="()=>state.deleteOperationStep(element.sequence)"/>
                                </Cell>
                            </Row>
                        </template>
                    </draggable>
                 </Table>
                 <hr/>
                <div class="md:grid md:gap-4 md:grid-cols-2">
                    <InputTextLookup name="Activity"
                        placeholder="Search Activity" class="flex-grow"
                        :value="state.data.add.activityLookupText"
                        @select="selected => state.data.add.activity = selected"
                        @input="value => state.data.add.activityLookupText = value"
                        :options="state.meta.activityChoices.map( option => ({
                            value: option.value,
                            title: option.title,
                            subtitle: option.subtitle,
                            figure: option.figure
                        }))"/>
                    <InputText name="Notes" 
                        placeholder="Notes" type="text"
                        :value="`${state.data.add.notes}`"
                        @input="value => state.data.add.notes = value"/>
                </div>
                <div class="flex justify-between mt-4">
                    <span class="my-auto  text-xs">
                        Activity choices: {{state.meta.activityChoices.length}} records found
                    </span>
                    <Button icon="add" class="my-auto border-gray-300 border"
                        @click="state.addOperationStep">Add</Button>
                </div>
            </Section>
        </div>
    </Modal>
</template>

<script>
import Modal from '@/components/Modal.vue';
import Section from '@/components/Section.vue';
import InputText from '@/components/InputText.vue';
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
        Modal, Section, InputText, InputSelect, 
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
                measureUnit: '',
                operationSteps: [],
                add: {
                    activity: '',
                    activityLookupText: '',
                    notes: ''
                }
            },
            meta: {
                materialTypeChoices: [],
                measureUnitChoices: [],
                activities: [],
                activityChoices: computed(()=> {
                    if (state.meta.costingMeasureChoice) {
                        const filtered = state.meta.activities.filter(
                            x => x.measure == state.meta.costingMeasureChoice.base_measure &&
                                x.measureUnit == state.data.measureUnit);
                        return filtered.map(obj=> ({
                            value: obj.id,
                            title: obj.name,
                            subtitle: obj.rate,
                            figure: obj.measure,
                        }));
                    } else return [];
                }),
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
                costingMeasureChoice: computed(()=> {
                    const a = state.meta.costingMeasureChoicesMapping.find(
                        x => x.key == state.data.materialType);
                    if (a) return a.value.find(y => y.value == state.data.costingMeasure);
                    else return null;
                }),
                getActivityById: id => {
                    const activity = state.meta.activityChoices.find(c=> c.value == id);
                    return (activity)? activity.title : '';
                }
            },
            clearData: ()=> {
                state.data = {
                    name: '', 
                    materialType: '',
                    costingMeasure: '',
                    measureUnit: '',
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
                if (state.data.measureUnit == '') errors.push('measure unit');
                if (errors.length > 0)
                    state.error = `The following fields must not be empty: ${errors.join(', ')}.`;
                else state.error = '';
                return errors.length > 0;
            },
            save: async ()=> {
                if (state.validate()) return;
                const request = {
                    name: state.data.name,
                    material_type: state.data.materialType,
                    costing_measure: state.data.costingMeasure,
                    measure_unit: state.data.measureUnit,
                    operation_steps: state.data.operationSteps.map(o=>({
                        sequence: o.sequence,
                        id: o.id, activity: o.activityId, notes: o.notes
                    }))};
                const response = await saveOperation(request);
                if (response) {
                    if (props.onAfterSave) props.onAfterSave();
                    emit('toggle', false);
                }
            },
            clearOperationStepForm: ()=> {
                state.data.add = {activity: null, activityLookupText: null, notes: ''};
            },
            validateAddOperationStep: ()=> {
                let errors = [];
                if (state.data.add.activity == '') errors.push('activity');
                if (errors.length > 0)
                    state.error = `The following fields must not be empty: ${errors.join(', ')}.`;
                else state.error = '';
                return errors.length > 0;
            },
            addOperationStep: ()=> {
                if (state.validateAddOperationStep()) return;
                const next_sequence = state.data.operationSteps.length + 1;
                state.data.operationSteps.push({
                    id: null, sequence: next_sequence, activityId: state.data.add.activity, 
                    activityName: state.meta.getActivityById(state.data.add.activity),
                    rate: null, notes: state.data.add.notes
                });
                state.clearOperationStepForm();
            },
            deleteOperationStep: (sequence)=> {
                state.data.operationSteps = state.data.operationSteps.filter(
                    s => s.sequence != sequence);
                state.updateOperationSteps();
            },
            updateOperationSteps: () => {
                state.data.operationSteps.forEach((step, key)=> {
                    state.data.operationSteps[key].sequence = key+1;
                })
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
                    state.data.measureUnit = response.measure_unit;
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

                state.meta.measureUnitChoices = 
                    response2.actions.POST.measure_unit.choices.map(x=> ({
                        value: x.value, label: x.display_name, measure: x.measure
                    }));

                const response3 = await WorkstationApi.retrieveWorkstationActivities(id);
                if (response3) {
                    state.meta.activities = response3.map(obj => ({
                        id: obj.id, name: obj.name, 
                        measure: obj.measure, 
                        measureUnit: obj.measure_unit,
                        rate: obj.speed.rate
                    }));
                }
            }
        }

        const retrieveOperationSteps = async (id)=> {
            state.isProcessing = true;
            if (id) {
                const response = await OperationApi.retrieveOperationSteps(id);
                if (response) {
                    state.data.operationSteps = response.map(obj=> ({
                        id: obj.id, sequence: obj.sequence, activityId: obj.activity.id,
                        activityName: obj.activity.name, rate: obj.activity.speed.rate,
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
            state.isProcessing = false;
            return response;
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