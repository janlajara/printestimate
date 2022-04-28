 <template>
    <Page :title="`Press : ${state.machine.data.name}`">
        <hr class="my-4"/>
        <div class="flex gap-4">
            <Button color="secondary" icon="arrow_back"
                @click="()=>$router.go(-1)">Go Back</Button>
            <Button class="my-auto" icon="edit"
                @click="state.machine.editModal.open"/>
            <Button icon="delete" 
                @click="state.machine.deleteDialog.open"/>
            <SheetFedPressMachineModal :machine-id="state.id"
                :is-open="state.machine.editModal.isOpen"
                @toggle="state.machine.editModal.toggle"
                :on-after-save="()=>retrieveMachineDetail(state.id)"/>
            <DeleteRecordDialog 
                heading="Delete Press"
                :is-open="state.machine.deleteDialog.isOpen"
                :execute="state.machine.deleteDialog.delete"
                :on-after-execute="()=>$router.go(-1)"
                @toggle="state.machine.deleteDialog.toggle">
                <div>
                    Are you sure you want to delete 
                    <span class="font-bold">
                        {{state.machine.data.name}}</span>?
                </div>
            </DeleteRecordDialog>
        </div>
        <Section>
            <DescriptionList class="md:grid-cols-4">
                <DescriptionItem :loader="state.isProcessing" 
                    name="Name" :value="state.machine.data.name"/>
                <DescriptionItem :loader="state.isProcessing" 
                    name="Type" :value="state.machine.data.type"/>
                <DescriptionItem :loader="state.isProcessing" 
                    name="Description" :value="state.machine.data.description"/>
            </DescriptionList>
        </Section>
        <Section heading="Sheet Settings">
            <DescriptionList class="md:grid-cols-4">
                <DescriptionItem :loader="state.isProcessing" 
                    name="Min~max Width" :value="state.machine.data.widthRange"/>
                <DescriptionItem :loader="state.isProcessing" 
                    name="Min~max Length" :value="state.machine.data.lengthRange"/>
            </DescriptionList>
        </Section>
        <!--Section heading="Press Sheets">
            <Tabs>
                <Tab title="Parent Sheets">
                    <ParentSheetList :machine-id="state.id"/>
                </Tab>
                <Tab title="Child Sheets">
                    <ChildSheetList :machine-id="state.id"/>
                </Tab>
            </Tabs>
        </Section-->
    </Page>
</template>

<script>
import Page from '@/components/Page.vue';
import Button from '@/components/Button.vue';
import Section from '@/components/Section.vue';
import DescriptionList from '@/components/DescriptionList.vue';
import DescriptionItem from '@/components/DescriptionItem.vue';
import DeleteRecordDialog from '@/components/DeleteRecordDialog.vue';
//import Tabs from '@/components/Tabs.vue';
//import Tab from '@/components/Tab.vue';

import SheetFedPressMachineModal from '@/views/admin/production/machines/sheetfedpress/SheetFedPressMachineModal.vue';
//import ParentSheetList from '@/views/admin/production/machines/sheetfedpress/parentsheets/ParentSheetList.vue';
//import ChildSheetList from '@/views/admin/production/machines/sheetfedpress/childsheets/ChildSheetList.vue';

import {useRoute} from 'vue-router';
import {reactive, onBeforeMount} from 'vue';
import {SheetFedPressMachineApi} from '@/utils/apis.js';

export default {
    components: {
        Page, Button, Section, DescriptionList, DescriptionItem, DeleteRecordDialog,
        SheetFedPressMachineModal //, ParentSheetList, ChildSheetList, Tabs, Tab,
    },
    setup() {
        const route = useRoute();
        const state = reactive({
            id: route.params.id,
            isProcessing: false,
            machine: {
                data: {
                    id: '', name: '', type: '', description: '', uom: '',
                    minLength: '', maxLength:'', minWidth: '', maxWidth: '',
                    lengthRange: '', widthRange: ''
                },
                editModal: {
                    isOpen: false,
                    toggle: value => state.machine.editModal.isOpen = value,
                    open: ()=> state.machine.editModal.toggle(true)
                },
                deleteDialog: {
                    isOpen: false,
                    toggle: value => state.machine.deleteDialog.isOpen = value,
                    open: ()=> state.machine.deleteDialog.toggle(true),
                    delete: ()=> deleteMachine(state.id)
                }
            }
        });

        const retrieveMachineDetail = async (id)=> {
            state.isProcessing = true;
            const response = await SheetFedPressMachineApi.retrieveSheetFedPressMachine(id);
            if (response) {
                state.machine.data = {
                    id: response.id,
                    name: response.name,
                    type: response.process_type,
                    description: response.description,
                    uom: response.uom,
                    minLength: response.min_sheet_length,
                    maxLength: response.max_sheet_length,
                    minWidth: response.min_sheet_width,
                    maxWidth: response.max_sheet_width,
                    lengthRange: response.length_range,
                    widthRange: response.width_range
                }
            }
            state.isProcessing = false;
        }

        const deleteMachine = async (id)=> {
            if (id) await SheetFedPressMachineApi.deleteSheetFedPressMachine(id); 
        }

        onBeforeMount(async ()=> {
            const id = state.id;
            if (id) retrieveMachineDetail(id);
        })

        return {
            state, retrieveMachineDetail, deleteMachine
        }
    }
}
</script>