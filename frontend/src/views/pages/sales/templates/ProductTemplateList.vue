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
            <Table :headers="['Name', 'Description']" :loader="state.isProcessing">
                <Row v-for="(s, key) in state.list" :key="key" clickable
                    @click="()=> goToDetail(s.id)">
                    <Cell label="Name">{{s.name}}</Cell>
                    <Cell label="Description">{{s.description}}</Cell>
                </Row>
            </Table>
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

import ProductTemplateModal from './ProductTemplateModal.vue';

import {useRouter} from 'vue-router';
import {reactive, onBeforeMount} from 'vue';
import {ProductTemplateApi} from '@/utils/apis.js';

export default {
    components: {
        Page, Section, Button, Table, Row, Cell, ProductTemplateModal
    },
    setup() {
        const router = useRouter();
        const state = reactive({
            isProcessing: false,
            list: [],
            createModal: {
                isOpen: false,
                toggle: (value)=> state.createModal.isOpen = value,
                open: ()=> state.createModal.toggle(true)
            }
        })

        const populateProductTemplateList = async ()=> {
            state.isProcessing = true;
            const response = await ProductTemplateApi.listProductTemplates();
            if (response) {
                state.list = response.map( obj => ({
                    id: obj.id,
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