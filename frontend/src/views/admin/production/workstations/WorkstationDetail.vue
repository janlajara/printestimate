 <template>
    <Page :title="`Workstation : ${state.workstation.validatedData.name}`">
        <hr class="my-4"/>
        <div class="flex gap-4">
            <Button color="secondary" icon="arrow_back"
                @click="()=>$router.go(-1)">Go Back</Button>
            <Button class="my-auto" icon="edit"
                @click="state.workstation.editModal.open"/>
            <Button icon="delete" 
                @click="state.workstation.deleteDialog.open"/>
            <WorkstationModal :workstation-id="state.id"
                :is-open="state.workstation.editModal.isOpen"
                @toggle="state.workstation.editModal.toggle"
                :on-after-save="()=>retrieveWorkstationDetail(state.id)"/>
            <DeleteRecordDialog 
                heading="Delete Workstation"
                :is-open="state.workstation.deleteDialog.isOpen"
                :execute="state.workstation.deleteDialog.delete"
                :on-after-execute="()=>$router.go(-1)"
                @toggle="state.workstation.deleteDialog.toggle">
                <div>
                    Are you sure you want to delete 
                    <span class="font-bold">
                        {{state.workstation.validatedData.name}}</span>?
                </div>
            </DeleteRecordDialog>
        </div>
        <Section>
            <DescriptionList class="grid-cols-2 md:grid-cols-4">
                <DescriptionItem :loader="state.isProcessing" 
                    name="Name" :value="state.workstation.validatedData.name"/>
            </DescriptionList>
        </Section>
        <Section heading="Configuration">
            <Tabs>
                <Tab title="Activity Expenses">
                    <ActivityExpenseList :workstation-id="parseInt(state.id)"/>
                </Tab>
                <Tab title="Activities">
                    <ActivityList :workstation-id="parseInt(state.id)"/>
                </Tab>
                <Tab title="Operations">
                    <OperationList :workstation-id="parseInt(state.id)"/>
                </Tab>
            </Tabs>
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
import Tabs from '@/components/Tabs.vue';
import Tab from '@/components/Tab.vue';

import WorkstationModal from '@/views/admin/production/workstations/WorkstationModal.vue';
import ActivityExpenseList from '@/views/admin/production/workstations/activityexpenses/ActivityExpenseList.vue';
import ActivityList from '@/views/admin/production/workstations/activities/ActivityList.vue'; 
import OperationList from '@/views/admin/production/workstations/operations/OperationList.vue'; 

import {useRoute} from 'vue-router';
import {reactive, computed, onBeforeMount} from 'vue';
import {WorkstationApi} from '@/utils/apis.js';

export default {
    components: {
        Page, Button, Section, DescriptionList, DescriptionItem, DeleteRecordDialog,
        Tabs, Tab, WorkstationModal, ActivityExpenseList, ActivityList, OperationList
    },
    setup() {
        const route = useRoute();
        const state = reactive({
            id: route.params.id,
            isProcessing: false,
            workstation: {
                rawData: {},
                validatedData: {
                    id: computed(()=>state.workstation.rawData.id),
                    name: computed(()=>state.workstation.rawData.name? 
                        state.workstation.rawData.name : '')
                },
                editModal: {
                    isOpen: false,
                    toggle: value => state.workstation.editModal.isOpen = value,
                    open: ()=> state.workstation.editModal.toggle(true)
                },
                deleteDialog: {
                    isOpen: false,
                    toggle: value => state.workstation.deleteDialog.isOpen = value,
                    open: ()=> state.workstation.deleteDialog.toggle(true),
                    delete: ()=> deleteWorkstation(state.id)
                }
            }
        });

        const retrieveWorkstationDetail = async (id)=> {
            state.isProcessing = true;
            const response = await WorkstationApi.retrieveWorkstation(id);
            if (response) {
                state.workstation.rawData = {
                    id: response.id,
                    name: response.name
                }
            }
            state.isProcessing = false;
        }

        const deleteWorkstation = async (id)=> {
            if (id) await WorkstationApi.deleteWorkstation(id); 
        }

        onBeforeMount(async ()=> {
            const id = state.id;
            if (id) retrieveWorkstationDetail(id);
        })

        return {
            state, retrieveWorkstationDetail, deleteWorkstation
        }
    }
}
</script>