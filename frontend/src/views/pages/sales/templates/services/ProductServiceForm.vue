<template>
    <div  v-if="state.service != null">
        <p class="font-bold">{{state.service.name}}</p>
        <div v-if="state.error" 
            class="pt-4 text-sm text-red-600">*{{state.error}}</div>
        <div class="md:grid md:gap-4 md:grid-cols-4">
            <InputSelect 
                v-for="(operation, key) in state.service.metaOperations" :key="key"
                :name="operation.name" class="flex-grow md:col-span-2"
                :multiple="operation.optionsType == 'Multiple'"
                :required="operation.isRequired"
                @input="(value)=> {
                    if (operation.optionsType != 'Multiple') value = [value] 
                    state.setValue(operation.id, value, key)}"
                :options="operation.metaOperationOptions.map(c=>{
                    let options = {
                        value: c.id, label: c.label,
                        isSelected: state.getValue(key)
                            .find(x => x.meta_operation_option == c.id) != null};
                    return options;
                })"/>
        </div>
    </div>
</template>
<script>
import InputSelect from '@/components/InputSelect.vue';
import {reactive, onMounted, onBeforeMount} from 'vue';

export default {
    props: {
        service: Object,
        value: Object
    },
    components: {
        InputSelect
    },
    emits: ['input', 'load'],
    setup(props, {emit}) { 
        const state = reactive({
            service: props.service,
            error: null,
            data: {
                id: null,
                meta_service: props.service.id,
                operation_templates: []
            },
            validate: ()=> {
                let errors = [];
                state.service.metaOperations.forEach((operation, key)=> {
                    const operationData = state.data.operation_templates[key]
                    if (operation.isRequired && 
                        operationData.operation_option_templates.length == 0)
                        errors.push(operation.name)
                });
                if (errors.length > 0)
                    state.error = `The following fields must not be empty: ${errors.join(', ')}.`;
                else state.error = '';
                return errors.length > 0;
            },
            setValue: (metaOperationId, value, index)=> {
                state.data.operation_templates[index] = {
                    meta_operation: metaOperationId, 
                    operation_option_templates: value.map(x=> ({
                        meta_operation_option: x
                    }))
                }
                emit('input', state.data);
            },
            getValue: (index)=> {
                const operation = state.data.operation_templates[index]
                return operation ? operation.operation_option_templates : []; 
            }
        });

        onBeforeMount(()=> {
            if (props.value) {
                state.data.id = props.value.id;
                state.data.operation_templates = props.value.operation_templates;
            } else if (state.service.metaOperations) {
                state.service.metaOperations.forEach((operation, key)=> {
                    state.data.operation_templates[key] = {
                        meta_operation: operation.id,
                        operation_option_templates: []}
                });
            }
        });
        onMounted(()=> {
            emit('load', {
                data: state.data,
                validator: state.validate
            });
        })

        return {
            state
        }
    }
}
</script>