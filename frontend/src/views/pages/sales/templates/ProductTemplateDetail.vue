  <template>
    <Page :title="`Product Template : ${state.data.name}`">
        <hr class="my-4"/>
        <div class="flex gap-4">
            <Button color="secondary" icon="arrow_back"
                @click="()=>$router.go(-1)">Go Back</Button>
            <Button class="my-auto" icon="edit"
                @click="state.components.editModal.open"/>
            <Button icon="delete" 
                @click="state.components.deleteDialog.open"/>
            <ProductTemplateModal 
                :product-template-id="state.id"
                :is-open="state.components.editModal.isOpen"
                @toggle="state.components.editModal.toggle" 
                :on-after-save="()=> retrieveProductTempalateDetail(state.id)"/>
            <DeleteRecordDialog 
                heading="Delete Product"
                :is-open="state.components.deleteDialog.isOpen"
                :execute="state.components.deleteDialog.delete"
                :on-after-execute="()=>$router.go(-1)"
                @toggle="state.components.deleteDialog.toggle">
                <div>
                    Are you sure you want to delete 
                    <span class="font-bold">
                        {{state.data.name}}</span>?
                </div>
            </DeleteRecordDialog>
        </div>
        <Section>
            <DescriptionList class="md:grid-cols-3">
                <DescriptionItem :loader="state.isProcessing" 
                    name="Code" :value="state.data.code"/>
                <DescriptionItem :loader="state.isProcessing" 
                    name="Name" :value="state.data.name"/>
                <DescriptionItem :loader="state.isProcessing" 
                    name="Description" :value="state.data.description"/>
            </DescriptionList>
        </Section>
        <div class="md:grid md:grid-cols-2 md:gap-6">
            <!--ProductServiceList 
                :product-services="state.data.serviceTemplates"/--> 
            <ServicesList
                :services="state.data.serviceTemplates"/>
            <Section heading="Components">
                <ProductComponentList 
                    :product-components="state.data.componentTemplates"/>
            </Section>
        </div>
    </Page>
</template>

<script>
import Page from '@/components/Page.vue';
import Button from '@/components/Button.vue';
import Section from '@/components/Section.vue';
import DescriptionList from '@/components/DescriptionList.vue';
import DescriptionItem from '@/components/DescriptionItem.vue';
import DeleteRecordDialog from '@/components/DeleteRecordDialog.vue';
import ProductComponentList from './components/ProductComponentList.vue';
import ServicesList from '../commons/ServicesList.vue';
import ProductTemplateModal from './ProductTemplateModal.vue';

import {useRoute} from 'vue-router';
import {reactive, onBeforeMount} from 'vue';
import {ProductTemplateApi} from '@/utils/apis.js';

export default {
    components: {
        Page, Button, Section, DescriptionList, DescriptionItem, DeleteRecordDialog,
        ProductComponentList, ServicesList, ProductTemplateModal
    },
    setup() {
        const route = useRoute();
        const state = reactive({
            id: route.params.id,
            isProcessing: false,
            data: {
                code: '',
                name: '',
                description: '',
                metaProduct: null,
                componentTemplates: [],
                serviceTemplates: []
            },
            components: {
                editModal: {
                    isOpen: false,
                    toggle: value => state.components.editModal.isOpen = value,
                    open: ()=> state.components.editModal.toggle(true)
                },
                deleteDialog: {
                    isOpen: false,
                    toggle: value => state.components.deleteDialog.isOpen = value,
                    open: ()=> state.components.deleteDialog.toggle(true),
                    delete: async ()=> await deleteMetaProduct(state.id)
                }
            }
        });

        const retrieveProductTempalateDetail = async (id)=> {
            state.isProcessing = true;
            const response = await ProductTemplateApi.retrieveProductTemplate(id);
            if (response) {
                state.data = {
                    code: response.code,
                    name: response.name,
                    description: response.description,
                    metaProduct: response.meta_product,
                    componentTemplates: response.component_templates,
                    serviceTemplates: response.service_templates.map(service => ({
                        name: service.name, sequence: service.sequence,
                        operations: service.operation_templates.map(ot => ({
                            name: ot.name,
                            material: null,
                            activities: ot.operation_option_templates.map(oot => ({
                                name: oot.label,
                                sequence: null,
                                speed: null,
                                notes: null
                            }))
                        }))
                    }))
                }
            }
            state.isProcessing = false;
        }

        const deleteMetaProduct = async (id)=> {
            if (id) await ProductTemplateApi.deleteProductTemplate(id); 
        }

        onBeforeMount(async ()=> {
            const id = state.id;
            if (id) retrieveProductTempalateDetail(id);
        })

        return {
            state, retrieveProductTempalateDetail
        }
    }
}
</script>