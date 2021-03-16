<template>
    <div>
        <dt class="text-sm font-bold text-gray-500">{{$props.name}}</dt>
        <dd class="mt-1" :class="(isBlank)? 'text-black text-opacity-30 italic': ''">
            {{(isBlank)? 'None' : $props.value}}
        </dd>
    </div>
</template>

<script>
import {computed} from 'vue';

export default {
    props: {
        name: String,
        value: String
    },
    setup(props) {
        const isBlank = computed(()=> props.value == null || props.value.trim() == '');
        return {
            isBlank
        }
    }
}
</script>