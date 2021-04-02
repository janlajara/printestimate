<template>
    <tr class="flex flex-wrap lg:table-row row bg-tertiary-light bg-opacity-30"
        :class="$props.clickable? 'hover:bg-secondary-light hover:bg-opacity-20 cursor-pointer': ''">
        <slot/>
    </tr>
</template>
<script>
export default {
    name: 'Row',
    props: {
        clickable: Boolean
    }
}
</script>