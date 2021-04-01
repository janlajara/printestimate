<template>
    <div class="flex rounded bg-tertiary-light bg-opacity-50">
        <input class="text-sm border-none focus:outline-none flex-grow bg-transparent" 
            type="text" v-model="search" @change="$emit('search', search)" 
            :disabled="$props.disabled" :placeholder="$props.placeholder"/>
        <span class="material-icons mx-4 my-auto">search</span>
    </div>
</template>

<script>
import {ref} from 'vue';

export default {
    props: {
        disabled: Boolean,
        placeholder: String
    },
    emits: ['search'],
    setup() {
        const search = ref('')
        return {
            search
        }
    }
}
</script>