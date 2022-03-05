<template>
    <div class="input">
        <label class="input-label">
          {{$props.name}}
          <span v-if="$props.required" 
                class="text-secondary-light">*</span>
        </label>
        <div class="rounded-md shadow-sm">
            <textarea class="rounded input-field w-full"
              :value="$props.value" :placeholder="$props.placeholder" 
              @input="event => $emit('input', event.target.value)">
            </textarea>
        </div>
    </div>
</template>

<script>

export default {
    props: {
        name: String,
        value: String,
        placeholder: String,
        required: Boolean
    },
    emits: ['input']
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
    @apply border-none bg-gray-200 text-sm;
  }
}

</style>