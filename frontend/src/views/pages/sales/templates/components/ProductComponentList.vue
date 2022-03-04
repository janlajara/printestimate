 <template>
    <div>
        <Table :loader="state.isProcessing"
            :headers="['Name', 'Material/s', 'Quantity']" >
            <Row v-for="(s, key) in state.data.productComponents" :key="key">
                <Cell label="Name">{{s.name}}</Cell>
                <Cell label="Material/s">
                    <ul class="pl-2 text-xs">
                        <li v-for="(x, i) in s.material_templates" :key="i"
                            class="list-disc">
                            {{x.item_name}} {{s.size}}
                        </li>
                    </ul>
                </Cell>
                <Cell label="Quantity">
                    <span v-if="s.material_templates.length > 1">
                        {{s.quantity}} x {{s.material_templates.length}}
                    </span>
                    <span v-else>
                        {{s.total_material_quantity}} 
                    </span>
                </Cell>
            </Row>
        </Table>
    </div>
</template>

<script>
import Table from '@/components/Table.vue';
import Row from '@/components/Row.vue';
import Cell from '@/components/Cell.vue';

import {reactive, computed} from 'vue';

export default {
    components: {
        Table, Row, Cell
    },
    props: {
        productComponents: {
            type: Array,
            default: ()=>[]
        }
    },
    setup(props) {
        const state = reactive({
            isProcessing: false,
            data: {
                productComponents: computed(()=>props.productComponents)
            },
        });

        return {
            state
        }
    }
}
</script>