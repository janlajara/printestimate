<template>
    <div class="input">
        <label class="input-label">{{$props.name}}</label>
        <slot/>
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
}
</style>