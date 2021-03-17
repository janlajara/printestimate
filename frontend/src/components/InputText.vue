<template>
    <div class="input">
        <label class="input-label">{{$props.name}}
            <span v-if="$props.required" 
                class="text-secondary-light">*</span>
            <span v-if="$props.disabled" 
                class="material-icons text-sm text-secondary-light">lock</span>
        </label>
        <div class="flex rounded-md shadow-sm">
            <span v-if="$props.prefix"
                class="input-field-part rounded-l-md">
                {{$props.prefix}}
            </span>
            <input :type="($props.type == 'password')? 'password': 'text'" 
                :placeholder="$props.placeholder"
                class="input-field w-full" :value="$props.value"
                :class="inputStyle" :disabled="$props.disabled"
                @input="(event)=>emitInput(event)"
                :readonly="$props.readonly"/>
            <span v-if="$props.postfix"
                class="input-field-part rounded-r-md">
                {{$props.postfix}}</span>
        </div>
    </div>
</template>

<script>
import {ref} from 'vue'

export default {
    emits: ['input'],
    props: {
        name: String,
        prefix: String,
        postfix: String,
        placeholder: String,
        value: {
            type: [String, Number]
        },
        type: {
            type: String,
            required: true,
            validator: (value) => {
                return ['text', 'number', 'decimal', 'password'].indexOf(value) !== -1
            }
        },
        required: Boolean,
        disabled: Boolean,
        readonly: Boolean,
    },
    setup(props, {emit}) {
        const inputStyle = ref([])

        if (!props.prefix && !props.postfix)
            inputStyle.value = ['rounded']
        else if (props.prefix && !props.postfix)
            inputStyle.value = ['rounded-r-md']
        else if (!props.prefix && props.postfix)
            inputStyle.value = ['rounded-l-md']
        if (props.disabled) {
            inputStyle.value.push('text-gray-400')
        }

        const emitInput = (event)=> {
            let input = event.target.value;
            if (props.type == 'number' || props.type == 'decimal') {
                if (props.type == 'decimal') {
                    const firstOccur = input.indexOf('.');
                    if (firstOccur >= 0) {
                        input = input.substr(0, firstOccur+1) + 
                            input.slice(firstOccur+1).replaceAll('.', '');
                    }
                }
                input = input.replace(/[^\d.]/g, "");
                if (input.trim() == "") input = null;
            }
            emit('input', input);
            event.target.value = input;
        }

        return {
            inputStyle, emitInput
        }
    }
}
</script>

<style scoped>
@layer components {
  .input {
    @apply mt-2;
  }

  .input-label {
    @apply text-sm font-medium;
  }

  .input-field {
    @apply border-none text-sm;
    @apply focus:outline-none;
  }

  .input-field-part {
    @apply inline-flex items-center px-2
  }

  .input-field, .input-field-part {
    @apply bg-gray-200 text-sm;
  }
}
</style>