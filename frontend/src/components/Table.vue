<template>
    <div class="my-4 rounded-md overflow-hidden">
        <table class="w-full" 
            :class="$props.layout == 'auto' ?
                'lg:table-auto' : 'lg:table-fixed'">
            <thead class="hidden lg:table-header-group">
                <tr class="flex flex-wrap lg:table-row row bg-primary-light bg-opacity-50">
                    <th v-for="(header, key) in $props.headers" :key="key" 
                        class="px-3 py-3 sm:px-6 text-left text-xs"
                        :class="columnsWidth ? columnsWidth[key] : null">
                        {{header}}</th>
                </tr>
            </thead>
            <slot v-if="$props.noBody"/>
            <tbody v-else class="bg-white divide-y divide-gray-200">
                <Row v-for="(row, key1) in $props.rows" :key="key1">
                    <Cell v-for="(col, key2) in row.splice(0, columnCount)" 
                        :key="key2" :label="$props.headers[key2]">
                        {{col}}
                    </Cell>
                </Row>
                <slot v-if="$slots.default && $slots.default()[0].children.length > 0"/>
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
        layout: {
            type: String,
            default: 'auto',
            validator: value => ['auto', 'fixed'].includes(value)
        },
        headers: {
            type: Array,
            required: true
        },
        colsWidth: Array,
        rows: Array,
        loader: Boolean,
        noBody: {
            type: Boolean,
            default: false
        }
    },
    setup(props) { 
        const columnCount = computed(()=> (props.headers? props.headers.length: 0));
        return {
            columnCount,
            columnsWidth: computed(()=> {
                let cw = null;
                if (props.layout == 'fixed' && props.colsWidth && 
                    props.colsWidth.length == props.headers.length) {
                        cw = props.colsWidth;
                }
                return cw;
            })
        }
    }
}
</script>
