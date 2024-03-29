<template>
    <div>
        <div class="grid gap-4 md:grid-cols-3">
            <InputSelect name="Machine Type"
                :disabled="state.machineForm.machines.length > 0"
                @input="value => {
                    state.machineForm.machineType = value;
                }"
                :options="state.meta.machineTypes.map(c=>({
                    value: c.value, label: c.label,
                    isSelected: state.machineForm.machineType == c.value
                }))"/>
            <InputSelect name="Machines" multiple class="md:col-span-2"
                :disabled="state.machineForm.machineType == null"
                @input="value => {
                    state.machineForm.machines = value;
                    state.emitInput();}"
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
                machineList: [],
                machineChoices: computed(()=> {
                    const filtered = state.meta.machineList.filter(x => 
                        x.materialtype == state.materialType &&
                        x.resourcetype == state.machineForm.machineType);
                    return filtered;
                }),
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
                material_type: state.materialType || ''
            }
            const response = await MachineApi.listMachines(filter); 
            if (response) {
                state.meta.machineList = response.map( x => ({
                    label: x.name, value: x.id,
                    materialtype: x.material_type,
                    resourcetype: x.resourcetype
                }));
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
        watch(()=> props.value, async ()=> {
            await listMachines();

            state.machineForm.machines = props.value.map(x => x.machine);
            const machines = state.machineForm.machines;
            if (machines.length > 0) {
                const m = state.meta.machineList.find(x => x.value == machines[0])
                if (m) state.machineForm.machineType = m.resourcetype;
            }
        });
        onBeforeMount(listMachineTypes);

        return {
            state, listMachines
        }
    }
}
</script>