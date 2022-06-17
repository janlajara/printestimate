<template>
    <td class="text-sm align-top block lg:table-cell" :colspan="$props.colspan">
        <label class="cell-label">{{$props.label}}</label>
        <span class="align-middle cell-value"><slot/></span>
    </td>
</template>

<script>
export default {
    name: 'Cell',
    props: ['label', 'colspan'],
}
</script>

<style scoped>
@layer components {
    .cell-label {
        @apply block lg:hidden;
        @apply font-bold text-xs text-secondary-dark;
    }
    td {
        @apply pt-3 pb-3; 
        @apply px-4 lg:px-6;
    }
    td:first-child {
        @apply w-full lg:w-auto;
        @apply pb-1;
    }
    td:first-child > label.cell-label {
        @apply hidden;
    }
    td:first-child > span.cell-value {
        @apply text-base lg:text-sm;
        @apply font-bold lg:font-normal;
        @apply text-primary lg:text-current;
    }
}
</style>