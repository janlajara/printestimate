<template>
    <div class="my-4 rounded-md overflow-hidden">
        <table class="table-auto w-full">
            <thead class="hidden lg:table-header-group">
                <tr class="flex flex-wrap lg:table-row row bg-primary-light bg-opacity-50">
                    <th v-for="(header, key) in $props.headers" :key="key" 
                        class="px-3 py-3 sm:px-6 text-left text-xs">{{header}}</th>
                </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
                <Row v-for="(row, key1) in $props.rows" :key="key1">
                    <Cell  v-for="(col, key2) in row.splice(0, columnCount)" 
                        :key="key2" :label="$props.headers[key2]">
                        {{col}}
                    </Cell>
                </Row>
                <slot v-if="$slots.default()[0].children.length > 0"/>
                <Row v-else-if="$props.loader">
                    <Cell :colspan="columnCount">
                        <div class="w-full flex justify-center">
                            <span class="material-icons animate-spin text-secondary-light">
                                autorenew
                            </span>
                        </div>
                    </Cell>
                </Row>
            </tbody>
        </table>
    </div>
</template>

<script>
import {computed} from 'vue'
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
        rows: Array,
        loader: Boolean
    },
    setup(props) {
        const columnCount = computed(()=> (props.headers? props.headers.length: 0));
        return {
            columnCount
        }
    }
}
</script>
