<template>
    <tr class="flex flex-wrap lg:table-row row bg-gray-50"
        :class="$props.select? 'hover:bg-secondary-light hover:bg-opacity-20 cursor-pointer': ''"
        @click="executeSelect">
        <slot/>
    </tr>
</template>
<script>
export default {
    name: 'Row',
    props: {
        select: Function
    },
    setup(props){
        const executeSelect = ()=> {
            if (props.select)
                props.select();
        };
        return {
            executeSelect
        }
    }
}
</script>