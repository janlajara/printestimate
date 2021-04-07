<template>
    <Page title="Inventory : Stock Requests">
        <hr class="my-4"/>
        <Section>
            <div class="space-y-4 md:space-x-4 md:space-y-0 md:flex md:justify-between">
                <div class="flex flex-grow">
                    <div class="my-auto">
                        <Button color="secondary" icon="add"
                            :action="()=>request.create.toggle(true)">
                            Create Request</Button>
                    </div>
                    <div class="grid flex-grow">
                        <SearchFilter class="justify-self-end"
                            label="Status Filter" 
                            @filter="(value)=> {
                                request.filter = value;
                                populateRequestList(request.listLimit, 0);}"
                            :options="[{label: 'All', value: ''}, 
                                {label: 'Open', value: 'open'}, 
                                {label: 'Closed', value: 'closed'}]"/>
                    </div>
                </div>
                <SearchField placeholder="Search" :disabled="request.isProcessing"
                    @search="(search)=> {
                        request.search = search;
                        populateRequestList(request.listLimit, 0);}"/>
            </div>
            <Table :headers="['Request Id', 'Status', 'Num. of Requests', 
                'Reason', 'Date Created']" :loader="request.isProcessing">
                <Row v-for="(r, key) in request.list" :key="key" clickable
                    @click="()=> goToDetail(r.id)">
                    <Cell label="Request Id">{{formatId(r.id)}}</Cell>
                    <Cell label="Status">{{r.status}}</Cell>
                    <Cell label="Num. of Requests">{{r.itemRequestCount}}</Cell>
                    <Cell label="Reason">{{r.reason}}</Cell>
                    <Cell label="Date Created">{{r.createdAt}}</Cell>
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
import SearchField from '@/components/SearchField.vue';
import SearchFilter from '@/components/SearchFilter.vue';
import Button from '@/components/Button.vue';

import {reactive, onBeforeMount} from 'vue';
import {useRouter} from 'vue-router';
import {ItemRequestGroupApi} from '@/utils/apis.js';
import {reference} from '@/utils/format.js';

export default {
    components: {
        Page, Section, Table, Row, Cell, TablePaginator, 
        SearchField, SearchFilter, Button, 
    },
    setup() {
        const router = useRouter();
        const request = reactive({
            isProcessing: false,
            list: [],
            listLimit: 5,
            listCount: 0,
            search: null,
            filter: null,
            create: {
                isOpen: false,
                toggle: (value)=> { 
                    request.create.isOpen = value
                }
            }
        });

        const populateRequestList = async (limit, offset)=> {
            request.isProcessing = true;
            const response = await ItemRequestGroupApi.listItemRequestGroups(
                limit, offset, request.search, request.filter);
            if (response && response.results) {
                request.listCount = response.count;
                request.list = response.results.map( r=> ({
                    id: r.id, status: r.status,
                    reason: r.reason, itemRequestCount: r.item_requests_count,
                    createdAt: r.created_at
                }));
            }
            request.isProcessing = false;
        };
        onBeforeMount(()=> {
            populateRequestList(request.listLimit, 0);
        });

        const goToDetail = (id)=> {
            router.push({ 
                name: 'inventory-stockrequest-detail', 
                params: {id}});
        };

        return {
            request, populateRequestList, goToDetail,
            formatId: (id)=> reference.formatId(id, reference.mrs)
        }
    }
}
</script>