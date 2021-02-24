<template>
    <div class="input">
        <label class="input-label">{{$props.name}}</label>
        <div class="flex rounded-md shadow-sm">
            <span v-if="$props.prefix"
                class="input-field-part rounded-l-md">
                {{$props.prefix}}</span>
            <input :type="$props.type" :placeholder="$props.placeholder"
                class="input-field flex-grow" :value="$props.value"
                :class="inputBorderStyle"/>
            <span v-if="$props.postfix"
                class="input-field-part rounded-r-md">
                {{$props.postfix}}</span>
        </div>
    </div>
</template>

<script>
import {ref} from 'vue'

export default {
    props: {
        name: String,
        prefix: String,
        postfix: String,
        placeholder: String,
        value: String,
        type: {
            type: String,
            required: true,
            validator: (value) => {
                return ['text', 'number', 'password'].indexOf(value) !== -1
            }
        },
        required: Boolean,
    },
    setup(props) {
        const inputBorderStyle = ref()

        if (!props.prefix && !props.postfix)
            inputBorderStyle.value = 'rounded'
        else if (props.prefix && !props.postfix)
            inputBorderStyle.value = 'rounded-r-md'
        else if (!props.prefix && props.postfix)
            inputBorderStyle.value = 'rounded-l-md'

        return {
            inputBorderStyle
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