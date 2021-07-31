  <template>
    <Page :title="`Product : ${state.metaProduct.validatedData.name}`">
        <hr class="my-4"/>
        <div class="flex gap-4">
            <Button color="secondary" icon="arrow_back"
                @click="()=>$router.go(-1)">Go Back</Button>
            <Button class="my-auto" icon="edit"
                @click="state.metaProduct.editModal.open"/>
            <Button icon="delete" 
                @click="state.metaProduct.deleteDialog.open"/>
            <MetaProductModal :meta-product-id="state.id"
                :is-open="state.metaProduct.editModal.isOpen"
                @toggle="state.metaProduct.editModal.toggle"
                :on-after-save="()=>retrieveMetaProductDetail(state.id)"/>
            <DeleteRecordDialog 
                heading="Delete Product"
                :is-open="state.metaProduct.deleteDialog.isOpen"
                :execute="state.metaProduct.deleteDialog.delete"
                :on-after-execute="()=>$router.go(-1)"
                @toggle="state.metaProduct.deleteDialog.toggle">
                <div>
                    Are you sure you want to delete 
                    <span class="font-bold">
                        {{state.metaProduct.validatedData.name}}</span>?
                </div>
            </DeleteRecordDialog>
        </div>
        <Section>
            <DescriptionList class="md:grid-cols-3">
                <DescriptionItem :loader="state.isProcessing" 
                    name="Name" :value="state.metaProduct.validatedData.name"/>
                <DescriptionItem :loader="state.isProcessing" 
                    name="Description" :value="state.metaProduct.validatedData.description"/>
            </DescriptionList>
        </Section>
        <Section heading="Components">
            <MetaComponentList :meta-product-id="parseInt(state.id)"/>
        </Section>
        <Section heading="Services">
        </Section>
    </Page>
</template>

<script>
import Page from '@/components/Page.vue';
import Button from '@/components/Button.vue';
import Section from '@/components/Section.vue';
import DescriptionList from '@/components/DescriptionList.vue';
import DescriptionItem from '@/components/DescriptionItem.vue';
import DeleteRecordDialog from '@/components/DeleteRecordDialog.vue';

import MetaProductModal from './MetaProductModal.vue';
import MetaComponentList from './metacomponents/MetaComponentList.vue';

import {useRoute} from 'vue-router';
import {reactive, computed, onBeforeMount} from 'vue';
import {MetaProductApi} from '@/utils/apis.js';

export default {
    components: {
        Page, Button, Section, DescriptionList, DescriptionItem, DeleteRecordDialog,
        MetaProductModal, MetaComponentList
    },
    setup() {
        const route = useRoute();
        const state = reactive({
            id: route.params.id,
            isProcessing: false,
            metaProduct: {
                rawData: {},
                validatedData: computed(()=>({
                    id: state.metaProduct.rawData.id,
                    name: state.metaProduct.rawData.name? 
                        state.metaProduct.rawData.name : '',
                    description: state.metaProduct.rawData.description,
                })),
                editModal: {
                    isOpen: false,
                    toggle: value => state.metaProduct.editModal.isOpen = value,
                    open: ()=> state.metaProduct.editModal.toggle(true)
                },
                deleteDialog: {
                    isOpen: false,
                    toggle: value => state.metaProduct.deleteDialog.isOpen = value,
                    open: ()=> state.metaProduct.deleteDialog.toggle(true),
                    delete: ()=> deleteMetaProduct(state.id)
                }
            }
        });

        const retrieveMetaProductDetail = async (id)=> {
            state.isProcessing = true;
            const response = await MetaProductApi.retrieveMetaProduct(id);
            if (response) {
                state.metaProduct.rawData = {
                    id: response.id,
                    name: response.name,
                    description: response.description
                }
            }
            state.isProcessing = false;
        }

        const deleteMetaProduct = async (id)=> {
            if (id) await MetaProductApi.deleteMetaProduct(id); 
        }

        onBeforeMount(async ()=> {
            const id = state.id;
            if (id) retrieveMetaProductDetail(id);
        })

        return {
            state, retrieveMetaProductDetail, deleteMetaProduct
        }
    }
}
</script>