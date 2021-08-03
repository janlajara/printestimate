 <template>
    <div>
        <Button icon="add" color="tertiary" :disabled="state.isProcessing"
            @click="()=>state.createEditModal.open()">Add Component</Button>
        <MetaComponentModal 
            :meta-product-id="state.id"
            :meta-component-id="state.createEditModal.data.id"
            :is-open="state.createEditModal.isOpen"
            @toggle="state.createEditModal.toggle" 
            :on-after-save="populateMetaComponents"/>
        <Table :headers="['Name', 'Type', '']" :loader="state.isProcessing">
            <Row v-for="(s, key) in state.list" :key="key" clickable>
                <Cell label="Name">{{s.name}}</Cell>
                <Cell label="Type" class="capitalize">{{s.type}}</Cell>
                <Cell>
                    <div class="w-full flex justify-end">
                        <Button class="my-auto" icon="edit"
                            @click="()=>state.createEditModal.open(s.id)"/>
                        <Button class="my-auto" icon="delete"
                            @click="()=>state.deleteDialog.open(s.id, s.name)"/>
                    </div>
                </Cell>
            </Row>
        </Table>
        <DeleteRecordDialog 
            heading="Delete Component"
            :is-open="state.deleteDialog.isOpen"
            :execute="state.deleteDialog.delete"
            :on-after-execute="populateMetaComponents"
            @toggle="state.deleteDialog.toggle">
            <div>
                Are you sure you want to delete 
                <span class="font-bold">
                    {{state.deleteDialog.data.name}}</span>?
            </div>
        </DeleteRecordDialog>
    </div>
</template>

<script>
import Table from '@/components/Table.vue';
import Row from '@/components/Row.vue';
import Cell from '@/components/Cell.vue';
import Button from '@/components/Button.vue';
import DeleteRecordDialog from '@/components/DeleteRecordDialog.vue';
import MetaComponentModal from './MetaComponentModal.vue';

import {reactive, onBeforeMount} from 'vue';
import {MetaProductApi, MetaComponentApi} from '@/utils/apis.js';

export default {
    components: {
        Table, Row, Cell, Button, DeleteRecordDialog, MetaComponentModal
    },
    props: {
        metaProductId: Number
    },
    setup(props) {
        const state = reactive({
            id: props.metaProductId,
            isProcessing: false,
            list: [],
            createEditModal: {
                isOpen: false,
                data: {
                    id: null
                },
                toggle: value => state.createEditModal.isOpen = value,
                open: (id) => {
                    state.createEditModal.data.id = id;
                    state.createEditModal.toggle(true);
                }
            },
            deleteDialog: {
                isOpen: false,
                data: {
                    id: null, name: null
                },
                toggle: value => state.deleteDialog.isOpen = value,
                open: (id, name) => {
                    state.deleteDialog.data = {id, name};
                    state.deleteDialog.toggle(true);
                },
                delete: async () => {
                    await deleteMetaComponent(state.deleteDialog.data.id);
                }
            }
        });

        const populateMetaComponents = async ()=> {
            state.isProcessing = true;
            if (state.id) {
                const response = await MetaProductApi.retrieveMetaProductComponents(state.id);
                if (response) {
                    state.list = response.map(obj=> ({
                        id: obj.id,
                        name: obj.name,
                        type: obj.type
                    }));
                }
            }
            state.isProcessing = false;
        }

        const deleteMetaComponent = async (id) => {
            state.isProcessing = true;
            if (id)  await MetaComponentApi.deleteMetaComponent(id);
            state.isProcessing = false;
        }

        onBeforeMount(populateMetaComponents);

        return {
            state, populateMetaComponents, deleteMetaComponent
        }
    }
}
</script>