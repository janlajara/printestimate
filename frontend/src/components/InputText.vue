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
            <input
                :type="($props.type == 'password')? 'password': 'text'" 
                :placeholder="$props.placeholder"
                class="input-field w-full" :value="$props.value"
                :class="[inputStyle, $props.disabled ? 'text-gray-400' : '']" 
                :disabled="$props.disabled"
                @blur="(event)=>emitInput(event)"
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
                return ['text', 'number', 'decimal', 'money', 'password'].indexOf(value) !== -1
            }
        },
        min: {
            type: Number,
            required: false
        },
        max: {
            type: Number,
            required: false
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

        const emitInput = (event)=> {
            let input = event.target.value;
            if (['number', 'decimal', 'money'].includes(props.type))  {
                let pattern = /[^\d]/g;
                if (['decimal', 'money'].includes(props.type)) {
                    const firstOccur = input.indexOf('.');
                    if (firstOccur >= 0) {
                        let whole = input.substr(0, firstOccur+1)
                        let decimal = input.slice(firstOccur+1).replaceAll('.', '');
                        if (props.type == 'money') decimal = decimal.substr(0, 2);
                        input = whole + decimal;
                    }
                    pattern = /[^\d.]/g;
                } 
                input = input.replace(pattern, "");
                if (input.trim() == "") {
                    input = null
                } else {
                    if (props.min != null && props.min > parseFloat(input)) input = props.min;
                    if (props.max != null && props.max < parseFloat(input)) input = props.max;
                }
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