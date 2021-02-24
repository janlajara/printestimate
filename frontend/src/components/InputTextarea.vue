<template>
    <div class="input">
        <label class="input-label">{{$props.name}}</label>
        <div class="rounded-md shadow-sm">
            <textarea class="rounded input-field w-full"></textarea>
        </div>
    </div>
</template>

<script>
export default {
    props: {
        name: String
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
    @apply border-none bg-gray-200 text-sm;
  }
}

</style>