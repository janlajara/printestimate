<template>
    <div>
        <div class="grid gap-4 md:grid-cols-3">
            <InputSelect name="Machine Type"
                @input="value => {
                    state.machineForm.machineType = value;
                }"
                :options="state.meta.machineTypes.map(c=>({
                    value: c.value, label: c.label,
                    isSelected: state.machineForm.machineType == c.value
                }))"/>
            <InputSelect name="Machines" multiple class="col-span-2"
                :disabled="state.machineForm.machineType == null"
                @input="value => {
                    state.machineForm.machines = value;
                    state.emitInput();
                }"
                :options="state.meta.machineChoices.map(c=>({
                    value: c.value, label: c.label,
                    isSelected: state.machineForm.machines.includes(c.value)
                }))"/>
        </div>
    </div>
</template>
<script>
import InputSelect from '@/components/InputSelect.vue';

import {reactive, computed, watch, onBeforeMount} from 'vue';
import {MachineApi} from '@/utils/apis.js';

export default {
    components: {
        InputSelect
    },
    props: {
        materialType: String,
        value: Array
    },
    emits: ['input'],
    setup(props, {emit}) {
        const state = reactive({
            materialType: computed(()=> props.materialType),
            machineForm: {
                id: null,
                machineType: null,
                machines: [],
            },
            meta: {
                machineTypes: [],
                machineChoices: [],
            },
            clearMachineForm: ()=> {
                state.machineForm = {
                    id: null,
                    machineType: null,
                    machines: [],
                }
            },
            emitInput: ()=> {
                const machineOptions = state.machineForm.machines.map( value => {
                    let id = null;
                    if (props.value) {
                        const machine = props.value.find(x => x.machine == value)
                        if (machine) id = machine.id;
                    }
                    return {
                        id: id,
                        machine: value
                    }
                });
                emit('input', machineOptions);
            }
        });

        const listMachines = async () => {
            const filter = {
                material_type: state.materialType || '',
                resourcetype: state.machineForm.machineType || ''
            }
            const response = await MachineApi.listMachines(filter);
            if (response) {
                state.meta.machineChoices = response.map( x => ({
                    label: x.name, value: x.id,
                }));
                state.machineForm.machineType = response[0].resourcetype;
            }
        }

        const listMachineTypes = async () => {
            const response = await MachineApi.listMachineTypes();
            if (response) {
                state.meta.machineTypes = response.map( x => ({
                    label: x.display, value: x.value
                }));
            }
        }

        watch(()=> state.materialType, ()=> {
            if (state.machineForm.machines.length > 0)
                state.machineForm.machines = [];
            listMachines();
        });
        watch(()=> props.value, ()=> {
            state.machineForm.machines = props.value.map(x => x.machine);
        });
        onBeforeMount(()=> {
            listMachineTypes();
            listMachines();
        });

        return {
            state, listMachines
        }
    }
}
</script>