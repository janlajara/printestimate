<template>
    <Page title="Admin : Production Workstations">
        <hr class="my-4"/>
        <div class="space-y-4 md:space-x-4 md:space-y-0 md:flex md:justify-between">
            <div class="my-auto">
                <Button color="secondary" icon="add"
                    :action="state.createModal.open">
                    Create Workstation</Button>
                <WorkstationModal :is-open="state.createModal.isOpen"
                    @toggle="state.createModal.toggle" 
                    :on-after-save="populateWorkstationList"/>
            </div>
        </div>
        <Section>
            <Table :headers="['Name', 'Description']" :loader="state.isProcessing">
                <Row v-for="(s, key) in state.list" :key="key" clickable
                    @click="()=> goToDetail(s.id)">
                    <Cell label="Name">{{s.name}}</Cell>
                    <Cell label="Name">{{s.description}}</Cell>
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

import WorkstationModal from '@/views/admin/production/workstations/WorkstationModal.vue';

import {useRouter} from 'vue-router';
import {reactive, onBeforeMount} from 'vue';
import {WorkstationApi} from '@/utils/apis.js';

export default {
    components: {
        Page, Section, Button, Table, Row, Cell, WorkstationModal
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

        const populateWorkstationList = async ()=> {
            state.isProcessing = true;
            const response = await WorkstationApi.listWorkstations();
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
                name: 'admin-production-workstation-detail', 
                params: {id}});
        };

        onBeforeMount(populateWorkstationList);

        return {
            state, goToDetail, populateWorkstationList
        }
    }
}
</script>