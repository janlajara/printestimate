<template>
    <button @click="$props.action"  :type="$props.type" :disabled="$props.disabled"
        :title="$refs.buttonText? $refs.buttonText.innerHTML : ''"
        class="flex px-3 py-1 font-bold" 
        :class="[buttonClass, $props.icon? 'rounded-full sm:rounded' : 'rounded']">
        <Icon v-if="$props.icon" :id="$props.icon" class="w-6 text-sm"/>
        <p v-if="$slots.default != null" class="w-full" :class="$props.icon? 'hidden sm:block' : ''" ref="buttonText">
            <slot/>
        </p>
    </button>
</template>

<script>
import {computed} from 'vue'
import Icon from '@/components/Icon.vue'

const button_styles_active = {
    'primary': 'bg-primary hover:bg-primary-light active:bg-primary-dark',
    'secondary': 'bg-tertiary hover:bg-tertiary-light active:bg-tertiary-dark',
    'none': 'hover:text-secondary'
}

const button_styles_disabled = {
    'primary': 'bg-primary text-black text-opacity-30',
    'secondary': 'bg-tertiary text-black text-opacity-30',
    'none': 'text-black text-opacity-30'
}

export default {
    components: {
        Icon
    },
    props: {
        icon: String,
        disabled: Boolean,
        type: {
            type: String,
            validator: (value) =>
                ['button', 'submit'].indexOf(value) !== -1
        },
        color: {
            type: String,
            validator: (value) => 
                ['primary', 'secondary'].indexOf(value) !== -1
        },
        action: {
            type: Function,
            required: false
        }
    },
    setup(props) { 
        const buttonClass = computed(()=> {
            let key = (props.color && 
                ['primary', 'secondary'].indexOf(props.color) != -1)?
                    props.color : 'none';

            let styles = (props.disabled)? 
                button_styles_disabled[key]:
                button_styles_active[key]

            return styles;
        });
        return { 
            buttonClass
        }
    }
}
</script>