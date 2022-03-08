 <template>
    <Page title="Sales : Products">
        <hr class="my-4"/>
        <div class="space-y-4 md:space-x-4 md:space-y-0 md:flex md:justify-between">
            <div class="my-auto">
                <Button color="secondary" icon="add"
                    :action="state.createModal.open">
                    Add Template</Button>
                <ProductTemplateModal 
                    :is-open="state.createModal.isOpen"
                    @toggle="state.createModal.toggle" 
                    :on-after-save="populateProductTemplateList"/>
            </div>
        </div>
        <Section>
            <Table :headers="['Code', 'Name', 'Description']" :loader="state.isProcessing">
                <Row v-for="(s, key) in state.list" :key="key" clickable
                    @click="()=> goToDetail(s.id)">
                    <Cell label="Code">{{s.code}}</Cell>
                    <Cell label="Name">{{s.name}}</Cell>
                    <Cell label="Description">{{s.description}}</Cell>
                </Row>
            </Table>
        </Section>
        <TablePaginator class="w-full justify-end"
            :limit="state.listLimit" :count="state.listCount"
            @change-limit="(limit)=> state.listLimit = limit"
            @change-page="({limit, offset})=> 
                populateProductTemplateList(limit, offset)" />
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

import ProductTemplateModal from './ProductTemplateModal.vue';

import {useRouter} from 'vue-router';
import {reactive, onBeforeMount} from 'vue';
import {ProductTemplateApi} from '@/utils/apis.js';

export default {
    components: {
        Page, Section, Button, Table, Row, Cell, ProductTemplateModal, TablePaginator
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

        const populateProductTemplateList = async (limit=10, offset=0)=> {
            state.isProcessing = true;
            const response = await ProductTemplateApi.listProductTemplates(limit, offset);
            if (response && response.results) {
                state.listCount = response.count;
                state.list = response.results.map( obj => ({
                    id: obj.id,
                    code: obj.code,
                    name: obj.name,
                    description: obj.description
                }))
            }
            state.isProcessing = false;
        }

        const goToDetail = (id)=> {
            router.push({ 
                name: 'sales-product-template-detail', 
                params: {id}});
        };

        onBeforeMount(populateProductTemplateList);

        return {
            state, goToDetail, populateProductTemplateList
        }
    }
}
</script>