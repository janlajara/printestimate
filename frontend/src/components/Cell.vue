<template>
    <td class="px-2 py-3 lg:px-6 text-sm align-top block lg:table-cell" :colspan="$props.colspan">
        <label class="font-bold text-xs block text-secondary-dark lg:hidden">
            {{$props.label}}</label>
        <span class="align-middle"><slot/></span>
    </td>
</template>

<script>
export default {
    name: 'Cell',
    props: ['label', 'colspan']
}
</script>