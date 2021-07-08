<template>
    <Modal :heading="`${state.isCreate ? 'Add' : 'Edit'} Activity`" 
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
            </div>
        </Section>
        <hr/>
        <Section heading="Speed" heading-position="side"> 
            <div class="md:grid md:gap-4 md:grid-cols-3">
                <InputText name="Value"  placeholder="Value"
                    type="decimal" :value="state.data.speed.measureValue" required
                    @input="value => state.data.speed.measureValue = value"/>
                <InputSelect name="Measure" required
                    @input="(value)=>state.data.speed.measureUnit = value"
                    :options="state.meta.measureUnitChoices.map(c=>({
                        value: c.value, label: c.label,
                        isSelected: state.data.speed.measureUnit == c.value
                    }))"/>
                <InputSelect name="Per" required
                    @input="(value)=>state.data.speed.speedUnit = value"
                    :options="state.meta.speedUnitChoices.map(c=>({
                        value: c.value, label: c.label,
                        isSelected: state.data.speed.speedUnit == c.value
                    }))"/>
            </div>
        </Section>
        <hr/>
        <Section heading="Overhead Time" heading-position="side"> 
            <div class="md:grid md:gap-4 md:grid-cols-3">
                <InputText name="Set-up"  placeholder="Set-up" 
                    :postfix="state.data.setUp.unit"
                    type="decimal" :value="state.data.setUp.value"
                    @input="value => state.data.setUp.value = value"/>
                <InputText name="Tear-down"  placeholder="Tear-down" 
                    :postfix="state.data.tearDown.unit"
                    type="decimal" :value="state.data.tearDown.value"
                    @input="value => state.data.tearDown.value = value"/>
            </div>
        </Section>
        <hr/>
        <Section heading="Expenses" heading-position="side"> 
        </Section>
    </Modal>
</template>

<script>
import Modal from '@/components/Modal.vue';
import Section from '@/components/Section.vue';
import InputText from '@/components/InputText.vue';
import InputSelect from '@/components/InputSelect.vue';

import {reactive, computed, watch, inject, onBeforeMount} from 'vue';
import {WorkstationApi, ActivityApi} from '@/utils/apis.js';

export default {
    components: {
        Modal, Section, InputText, InputSelect
    },
    props: {
        isOpen: Boolean,
        activityId: Number,
        workstationId: Number,
        onAfterSave: Function
    },
    emits: ['toggle'],
    setup(props, {emit}) { 
        const currency = inject('currency');
        const state = reactive({
            id: computed(()=>props.activityId),
            workstationId: computed(()=>props.workstationId),
            isCreate: computed(()=> state.id == null),
            isProcessing: false,
            error: '',
            data: {
                name: '', 
                speed: {
                    measureValue: '',
                    measureUnit: '',
                    speedUnit: '',
                }, 
                setUp: {
                    value: 0, unit: 'hr'},
                tearDown: {
                    value: 0, unit: 'hr'}
            },
            meta: {
                measureUnitChoices: [],
                speedUnitChoices: [],
            },
            clearData: ()=> {
                state.data = {
                    name: '', 
                    speed: {
                        measureValue: '',
                        measureUnit: '',
                        speedUnit: '',
                    }, 
                    setUp: {
                        value: 0, unit: 'hr'},
                    tearDown: {
                        value: 0, unit: 'hr'}
                }
            },
            validate: ()=> {
                let errors = [];
                if (state.data.name == '' || state.data.name == null) 
                    errors.push('name');
                if (state.data.speed.measureValue == '' ||
                        state.data.speed.measureUnit == '' ||
                        state.data.speed.speedUnit == '') errors.push('speed');
                if (errors.length > 0)
                    state.error = `The following fields must not be empty: ${errors.join(', ')}.`;
                else state.error = '';
                return errors.length > 0;
            },
            save: ()=> {
                if (state.validate()) return;
                const request = {
                    name: state.data.name,
                    speed: {
                        measure_value: state.data.speed.measureValue,
                        measure_unit: state.data.speed.measureUnit,
                        speed_unit: state.data.speed.speedUnit
                    },
                    set_up: `${state.data.setUp.value} ${state.data.setUp.unit}`,
                    tear_down: `${state.data.tearDown.value} ${state.data.tearDown.unit}`
                }
                saveActivity(request);
            }
        })

        const retrieveActivity = async (id) => {
            state.isProcessing = true;
            if (id) {
                const response = await ActivityApi.retrieveActivity(id);
                if (response) {
                    const setupSplit = response.set_up.split(' ');
                    const teardownSplit = response.tear_down.split(' ');
                    state.data = {
                        name: response.name, 
                        speed: {
                            measureValue: response.speed.measure_value,
                            measureUnit: response.speed.measure_unit,
                            speedUnit: response.speed.speed_unit}
                    }
                    if (setupSplit != null && setupSplit.length == 2) {
                        state.data.setUp = {
                            value: setupSplit[0],
                            unit: setupSplit[1]
                        }
                    }
                    if (teardownSplit != null && teardownSplit.length == 2) {
                        state.data.tearDown = {
                            value: teardownSplit[0],
                            unit: teardownSplit[1]
                        }
                    }
                }
            }
            state.isProcessing = false;
        }

        const retrieveMetaData = async () => {
            if (state.workstationId) {
                const response = await WorkstationApi.retrieveWorkstationActivities(
                    state.workstationId, true);
                state.meta.measureUnitChoices = 
                    response.actions.POST.speed.children.measure_unit.choices.map(c=> ({
                        value: c.value, label: c.display_name
                    }));
                state.meta.speedUnitChoices = 
                    response.actions.POST.speed.children.speed_unit.choices.map(c=> ({
                        value: c.value, label: c.display_name
                    }));
            }
        }

        const saveActivity = (activity) => {
            state.isProcessing = true;
            let response = null;
            if (state.isCreate) {
                response = WorkstationApi.createWorkstationActivity(
                    state.workstationId, activity);
            } else {
                response = ActivityApi.updateActivity(
                    state.id, activity);
            }
            if (response) {
                if (props.onAfterSave) props.onAfterSave();
                emit('toggle', false)
            }
            state.isProcessing = false;
        }

        watch(()=> [props.isOpen], ()=> {
            if (props.isOpen) {
                if (!state.isCreate) retrieveActivity(state.id);
                else state.clearData();
                state.error = '';
            }
        })
        onBeforeMount(()=> {
            retrieveMetaData();
        })

        return {
            state, currency
        }
    }
}
</script>