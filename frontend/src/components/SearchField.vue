<template>
    <div class="flex rounded border-b-2 border-primary-light shadow">
        <input class="text-sm border-none focus:outline-none flex-grow" 
            type="text" v-model="search" @change="$emit('search', search)" 
            :disabled="$props.disabled" :placeholder="$props.placeholder"/>
        <span class="material-icons mx-4 my-auto text-tertiary">search</span>
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