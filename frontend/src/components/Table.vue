<template>
    <div class="my-4 rounded-md overflow-hidden">
        <table class="table-auto">
            <thead class="hidden lg:table-header-group">
                <Row class="bg-primary-light bg-opacity-50">
                    <th v-for="(header, key) in $props.headers" :key="key" 
                        class="px-3 py-3 sm:px-6 text-left text-xs">{{header}}</th>
                </Row>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
                <Row v-for="(row, key1) in $props.rows" :key="key1">
                    <Cell  v-for="(col, key2) in row.splice(0, columnCount)" 
                        :key="key2" :label="$props.headers[key2]">
                        {{col}}
                    </Cell>
                </Row>
                <slot/>
            </tbody>
        </table>
    </div>
</template>

<script>
import {computed, ref} from 'vue'
import Row from '@/components/Row.vue'
import Cell from '@/components/Cell.vue'

export default {
    components: {
        Row, Cell
    },
    props: {
        headers: {
            type: Array,
            required: true
        },
        rows: Array
    },
    setup(props){
        const columnCount = computed(()=> props.headers.length)
        const tableRows = ref([])

        return {
            columnCount,
            tableRows
        }
    }
}
</script>
