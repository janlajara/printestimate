 <template>
    <div>
        <Button icon="add" color="tertiary" :disabled="state.isProcessing"
            @click="()=>state.createEditModal.open()">Add Service</Button>
        <MetaServiceModal  
            :meta-product-id="state.id"
            :meta-service-id="state.createEditModal.data.id"
            :meta-component-list="$props.metaComponentList"
            :is-open="state.createEditModal.isOpen"
            @toggle="state.createEditModal.toggle" 
            :on-after-save="populateMetaService"/>
        <Table :headers="['Name', 'Type', 'Costing Measure', 'Operations', '']" 
                :no-body="true">
            <draggable v-model="state.list" tag="tbody" 
                item-key="id" handle=".drag" @change="state.updateServiceSequence"
                class="bg-white divide-y divide-gray-200">
                <template #item="{element}">
                    <Row class="drag cursor-move">
                        <Cell label="Name">
                            <span class="material-icons text-xs my-auto">drag_indicator</span>
                            {{element.name}}</Cell>
                        <Cell label="Type" class="capitalize">
                            {{element.type}}</Cell>
                        <Cell label="Costing Measure" class="capitalize">
                            {{element.costingMeasure}}</Cell>
                        <Cell label="Operations">
                            <ul class="pl-2">
                                <li v-for="(x, i) in element.metaOperations" :key="i"
                                    class="list-disc">
                                    {{x.name}}
                                </li>
                            </ul>
                        </Cell>
                        <Cell>
                            <div class="w-full flex justify-end">
                                <Button class="my-auto" icon="edit"
                                    @click="()=>state.createEditModal.open(element.id)"/>
                                <Button class="my-auto" icon="delete"
                                    @click="()=>state.deleteDialog.open(element.id, element.name)"/>
                            </div>
                        </Cell>
                    </Row>
                </template>
            </draggable>
        </Table>
        <DeleteRecordDialog 
            heading="Delete Service"
            :is-open="state.deleteDialog.isOpen"
            :execute="state.deleteDialog.delete"
            :on-after-execute="populateMetaService"
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
import MetaServiceModal from './MetaServiceModal.vue';
import draggable from 'vuedraggable';

import {reactive, onBeforeMount} from 'vue';
import {MetaProductApi, MetaServiceApi} from '@/utils/apis.js';

export default {
    components: {
        Table, Row, Cell, Button, DeleteRecordDialog, MetaServiceModal, draggable
    },
    props: {
        metaProductId: Number,
        metaComponentList: Array
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
                    await deleteMetaService(state.deleteDialog.data.id);
                }
            },
            updateServiceSequence: ()=> {
                const serviceSequences = state.list.map((x, index) => ({
                    id: x.id, sequence: index+1
                }));
                updateMetaServiceSequences(state.id, serviceSequences);
            }
        });

        const populateMetaService = async ()=> {
            state.isProcessing = true;
            if (state.id) {
                const response = await MetaProductApi.retrieveMetaProductServices(state.id);
                if (response) {
                    state.list = response.map(obj=> ({
                        id: obj.id,
                        name: obj.name,
                        type: obj.type,
                        costingMeasure: obj.costing_measure,
                        metaOperations: obj.meta_operations
                    }));
                }
            }
            state.isProcessing = false;
        }

        const deleteMetaService = async (id) => {
            state.isProcessing = true;
            if (id)  await MetaServiceApi.deleteMetaService(id);
            state.isProcessing = false;
        }

        const updateMetaServiceSequences = async (id, sequences) => {
            state.isProcessing = true;
            if (id) {
                const response = await MetaProductApi.updateMetaServiceSequence(id, sequences);
                console.log(response)
            }
            state.isProcessing = false;
        }

        onBeforeMount(populateMetaService);

        return {
            state, populateMetaService
        }
    }
}
</script>