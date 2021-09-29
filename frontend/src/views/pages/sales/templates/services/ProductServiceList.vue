 <template>
    <div>
        <Table :loader="state.isProcessing"
            :headers="['#', 'Name', 'Operation/s']" >
            <Row v-for="(s, key) in state.data.productServices" :key="key">
                <Cell label="#">{{key+1}}</Cell>
                <Cell label="Name">{{s.name}}</Cell>
                <Cell label="Operation/s">
                    <p v-for="(x, i) in s.operation_templates" :key="i">
                        <span class="font-bold">{{x.name}}</span>:
                        <span class="pl-2">{{x.operation_option_templates.map(y=> y.label).join(',')}}</span>
                    </p>
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
        productServices: {
            type: Array,
            default: ()=>[]
        }
    },
    setup(props) {
        const state = reactive({
            isProcessing: false,
            data: {
                productServices: computed(()=>props.productServices)
            },
        });

        return {
            state
        }
    }
}
</script>