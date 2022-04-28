<template>
    <div>
        <div class="space-y-4 md:space-x-4 md:space-y-0 md:flex md:justify-between">
            <div class="my-auto">
                <Button color="secondary" icon="add"
                    :action="state.createModal.open">
                    Add Press</Button>
                <SheetFedPressMachineModal :is-open="state.createModal.isOpen"
                    @toggle="state.createModal.toggle" 
                    :on-after-save="populateMachines"/>
            </div>
        </div>
        <Section>
            <Table :headers="['Name', 'Type', 'Description']" :loader="state.isProcessing">
                <Row v-for="(s, key) in state.list" :key="key" clickable
                    @click="()=> goToDetail(s.id)">
                    <Cell label="Name">{{s.name}}</Cell>
                    <Cell label="Type">{{s.type}}</Cell>
                    <Cell label="Description">{{s.description}}</Cell>
                </Row>
            </Table>
        </Section>
    </div>
</template>
<script>
import Section from '@/components/Section.vue';
import Button from '@/components/Button.vue';
import Table from '@/components/Table.vue';
import Row from '@/components/Row.vue';
import Cell from '@/components/Cell.vue';
import SheetFedPressMachineModal from '@/views/admin/production/machines/sheetfedpress/SheetFedPressMachineModal.vue';

import {reactive, onBeforeMount} from 'vue';
import {useRouter} from 'vue-router';
import {SheetFedPressMachineApi} from '@/utils/apis.js';

export default {
    components: {
        Section, Button, Table, Row, Cell, SheetFedPressMachineModal
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
        });

        const populateMachines = async ()=> {
            state.isProcessing = true;
            const response = await SheetFedPressMachineApi.listSheetFedPressMachines();
            if (response) {
                state.list = response.map( obj => ({
                    id: obj.id,
                    name: obj.name,
                    description: obj.description,
                    type: obj.process_type
                }))
            }
            state.isProcessing = false;
        }

        const goToDetail = (id)=> {
            router.push({ 
                name: 'admin-production-sheetfedpressmachine-detail', 
                params: {id}});
        };

        onBeforeMount(()=> {
            populateMachines();
        })

        return {
            state, goToDetail, populateMachines
        }
    }
}
</script>