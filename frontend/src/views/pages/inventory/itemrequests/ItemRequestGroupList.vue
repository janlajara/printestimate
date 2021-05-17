<template>
    <Page title="Inventory : Item Requests">
        <hr class="my-4"/>
        <Section>
            <div class="space-y-4 md:space-x-4 md:space-y-0 md:flex md:justify-between">
                <div class="flex flex-grow">
                    <div class="my-auto">
                        <ItemRequestGroupModal 
                            :is-open="request.create.isOpen"
                            @toggle="request.create.toggle"/>
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
                            :options="[ 
                                {label: 'Open', value: 'open'}, 
                                {label: 'Closed', value: 'closed'},
                                {label: 'All', value: ''}]"/>
                    </div>
                </div>
                <SearchField placeholder="Search by Id, Reason..." 
                    :disabled="request.isProcessing"
                    @search="(search)=> {
                        request.search = search;
                        populateRequestList(request.listLimit, 0);}"/>
            </div>
            <Table layout="fixed"
                :headers="['Request Id', 'Status', 'Progress', 
                    'Reason', 'Date Created']" 
                :cols-width="['w-1/5', 'w-1/6', 'w-1/4', 'w-1/3', 'w-1/4']"
                :loader="request.isProcessing">
                <Row v-for="(r, key) in request.list" :key="key" clickable
                    @click="()=> goToDetail(r.id)">
                    <Cell label="Request Id">{{formatId(r.id)}}</Cell>
                    <Cell label="Status">{{r.status}}</Cell>
                    <Cell label="Progress">
                        <ProgressBar :percent="r.progressRate * 100" 
                            color="variable" class="pt-1">
                            {{formatPercentage(r.progressRate)}}
                        </ProgressBar>
                    </Cell>
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
import ProgressBar from '@/components/ProgressBar.vue';
import ItemRequestGroupModal from '@/views/pages/inventory/itemrequests/ItemRequestGroupModal.vue';

import {reactive, onBeforeMount} from 'vue';
import {useRouter} from 'vue-router';
import {ItemRequestGroupApi} from '@/utils/apis.js';
import {formatNumber, reference} from '@/utils/format.js';

export default {
    components: {
        Page, Section, Table, Row, Cell, TablePaginator, 
        SearchField, SearchFilter, Button, ProgressBar,
        ItemRequestGroupModal
    },
    setup() {
        const router = useRouter();
        const request = reactive({
            isProcessing: false,
            list: [],
            listLimit: 5,
            listCount: 0,
            search: null,
            filter: 'Open',
            create: {
                isOpen: false,
                toggle: (value)=> { 
                    request.create.isOpen = value
                },
                open: ()=> {
                    request.create.toggle(true); 
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
                    progressRate: r.progress_rate,
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
                name: 'inventory-itemrequest-detail', 
                params: {id}});
        };

        return {
            request, populateRequestList, goToDetail,
            formatId: (id)=> reference.formatId(id, reference.mrs),
            formatPercentage: (rate)=> `${formatNumber(rate * 100, 0)}%`
        }
    }
}
</script>