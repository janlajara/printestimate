<template>
    <Page title="Inventory : Stock Requests">
        <hr class="my-4"/>
        <Section>
            <Table :headers="['Request #', 'Status', 'Reason', 
                        'Date Created']"
                        :loader="request.isProcessing">
                    <Row v-for="(i, key) in request.list" :key="key">
                        <Cell label="Request #"></Cell>
                        <Cell label="Status"></Cell>
                        <Cell label="Reason"></Cell>
                        <Cell label="Date Created"></Cell>
                    </Row>
                </Table>
                <TablePaginator class="w-full justify-end"
                    :limit="request.listLimit" :count="request.listCount"
                    @change-limit="(limit)=> request.listLimit = limit"
                    @change-page="({limit, offset})=> 
                        populateRequestList(limit, offset)" />
        </Section>
    </Page>
</template>

<script>
import Page from '@/components/Page.vue';
import Section from '@/components/Section.vue';
import Table from '@/components/Table.vue';
import Row from '@/components/Row.vue';
import Cell from '@/components/Cell.vue';
import TablePaginator from '@/components/TablePaginator.vue';

import {reactive} from 'vue'

export default {
    components: {
        Page, Section, Table, Row, Cell, TablePaginator
    },
    setup() {
        const request = reactive({
            isProcessing: false,
            list: [],
            listLimit: 5,
            listCount: 0,
        })
        const populateRequestList = (offset, limit)=> {
            console.log(offset, limit)
        }
        return {
            request, populateRequestList
        }
    }
}
</script>