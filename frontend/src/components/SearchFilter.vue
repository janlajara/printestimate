<template>
    <div class="flex space-x-2 text-xs">
        <span v-if="$props.label" class="my-auto">{{$props.label}}:</span>
        <select @input="(event)=>$emit('filter', event.target.value)"
            class="rounded border-none bg-tertiary-light 
                bg-opacity-50 text-xs">
            <option v-for="(o, i) in $props.options" :key="i" 
                :value="o.value">
                {{o.label}}
            </option>
        </select>
    </div>
</template>
<script>

export default {
    props: {
        label: String,
        options: {
            type: Array,
            required: true
        }
    },
    emits: ['filter']
}
</script>