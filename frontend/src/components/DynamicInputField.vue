<template>
    <component 
        :is="state.attribute.inputComponent" 
        :required="state.attribute.required"
        :name="state.attribute.label" 
        :type="state.attribute.inputType"
        @input="value => state.value = value"
        :value="$props.value"
        :options="state.meta.options"/>
</template>
<script>
import InputText from '@/components/InputText.vue';
import InputSelect from '@/components/InputSelect.vue';
import {reactive, computed, watch, onMounted} from 'vue';

export default {
    props: {
        value: {
            type: [String, Number, Object],
            default: null
        },
        attribute: Object
    },
    components: {
        InputSelect, InputText
    },
    emits: ['input', 'load'],
    setup(props, {emit}) {
        const state = reactive({
            attribute: props.attribute || {},
            value: props.value,
            meta: {
                options: computed(()=> {
                    let options = []
                    if (state.attribute && state.attribute.options) {
                        options = state.attribute.options.map(option => {
                            return {
                                value: option.value,
                                label: option.label,
                                isSelected: option.value == state.value
                            }
                        })
                    }
                    return options;
                })
            }
        })
        watch(()=>state.value, ()=> {
            emit('input', state.value);
        })
        onMounted(()=> {
            emit('load', state.value);
        })
        return {
            state
        }
    }
}
</script>