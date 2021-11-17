 <template>
    <div>
        <Table :loader="state.isProcessing"
            :headers="['Name', 'Type', 'Size', 'Quantity', 'Material/s', 'Machine']" >
            <Row v-for="(s, key) in state.data.productComponents" :key="key">
                <Cell label="Name">{{s.name}}</Cell>
                <Cell label="Type" class="capitalize">{{s.type}}</Cell>
                <Cell label="Size">{{s.size}}</Cell>
                <Cell label="Quantity">
                    {{s.total_material_quantity}} 
                    <span v-if="s.material_templates.length > 1">
                        ({{s.quantity}} x {{s.material_templates.length}})
                    </span>    
                </Cell>
                <Cell label="Material/s">
                    <ul class="pl-2">
                        <li v-for="(x, i) in s.material_templates" :key="i"
                            class="list-disc">
                            {{x.label}}
                        </li>
                    </ul>
                </Cell>
                <Cell label="Machine">
                    {{s.machine_option_obj? s.machine_option_obj.name : ''}}</Cell>
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