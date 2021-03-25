<template>
    <div class="flex pr-4 mt-2">
        <div class="self-end pr-4"
            :class="$slots.default? 'items-start pt-2' : 'items-center'">
            <input type="checkbox" class="input-checkbox" 
                :value="$props.value" 
                @change="(event)=>$emit('input', event.target.checked)"/>
        </div>
        <div v-if="$props.label" class="self-end">
            <label class="input-label">{{$props.label}}</label>
            <p v-if="$slots.default" class="text-sm font-medium text-justify">
                <slot/>
            </p>
        </div>
    </div>
</template>

<script>
export default {
    props: {
        value: Boolean,
        label: String
    },
    emits: ['input']
}
</script>

<style scoped>
@layer components {
  .input-label {
    @apply text-sm font-medium;
  }

  .input-checkbox {
    @apply border-none rounded bg-gray-300 text-primary;
  }

  .input-checkbox:checked {
    @apply bg-checkbox;
  }
}
</style>