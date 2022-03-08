 <template>
    <Page title="Sales : Estimates">
        <hr class="my-4"/>
        <div class="space-y-4 md:space-x-4 md:space-y-0 md:flex md:justify-between">
            <div class="my-auto">
                <Button color="secondary" icon="add"
                    :action="state.createModal.open">
                    Create Estimate</Button>
                <EstimateModal 
                    :is-open="state.createModal.isOpen"
                    @toggle="state.createModal.toggle" 
                    @saved="estimateId => goToDetail(estimateId)"/>
            </div>
        </div>
        <Section>
            <Table :headers="['Name', 'Description', 'Template', 'Order Quantities']" :loader="state.isProcessing">
                <Row v-for="(s, key) in state.list" :key="key" clickable
                    @click="()=> goToDetail(s.id)">
                    <Cell label="Name">{{s.name}}</Cell>
                    <Cell label="Description">{{s.description}}</Cell>
                    <Cell label="Template">{{s.templateCode}}</Cell>
                    <Cell label="OrderQuantities">{{s.orderQuantities}}</Cell>
                </Row>
            </Table>
            <TablePaginator class="w-full justify-end"
                :limit="state.listLimit" :count="state.listCount"
                @change-limit="(limit)=> state.listLimit = limit"
                @change-page="({limit, offset})=> 
                    populateEstimateList(limit, offset)" />
        </Section>
    </Page>
</template>

<script>
import Page from '@/components/Page.vue';
import Section from '@/components/Section.vue';
import Button from '@/components/Button.vue';
import Table from '@/components/Table.vue';
import Row from '@/components/Row.vue';
import Cell from '@/components/Cell.vue';
import TablePaginator from '@/components/TablePaginator.vue';

import EstimateModal from './EstimateModal.vue';

import {useRouter} from 'vue-router';
import {reactive, onBeforeMount} from 'vue';
import {EstimateApi} from '@/utils/apis.js';

export default {
    components: {
        Page, Section, Button, Table, Row, Cell, EstimateModal, TablePaginator
    },
    setup() {
        const router = useRouter();
        const state = reactive({
            isProcessing: false,
            list: [],
            listLimit: 10,
            listCount: 0,
            createModal: {
                isOpen: false,
                toggle: (value)=> state.createModal.isOpen = value,
                open: ()=> state.createModal.toggle(true)
            }
        })

        const populateEstimateList = async (limit=10, offset=0)=> {
            state.isProcessing = true;
            const response = await EstimateApi.listEstimates(limit, offset);
            if (response && response.results) {
                state.listCount = response.count;
                state.list = response.results.map( obj => ({
                    id: obj.id,
                    name: obj.name,
                    description: obj.description,
                    templateCode: obj.template_code,
                    orderQuantities: obj.order_quantities.join(', ')
                }))
            }
            state.isProcessing = false;
        }

        const goToDetail = (id)=> {
            router.push({ 
                name: 'sales-product-estimates-detail', 
                params: {id}});
        };

        onBeforeMount(async ()=>{
            await populateEstimateList(state.listLimit, 0);
        });

        return {
            state, goToDetail, populateEstimateList
        }
    }
}
</script>