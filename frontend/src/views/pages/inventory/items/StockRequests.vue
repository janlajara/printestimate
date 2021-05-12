<template>
    <Section>
        <Table :loader="requests.isProcessing"
            :headers="['Request Id', 'Total Quantity', 'Status', 'Reason', 'Date Created']">
            <Row v-for="(request, key) in requests.list" :key="key">
                <Cell label="Request Id">
                    <Href @click="()=>
                        $router.push({ 
                            name: 'inventory-itemrequest-detail', 
                            params: {id: request.id}})">
                        {{reference.formatId(
                            request.id, reference.mrs)}}
                    </Href>
                </Cell>
                <Cell label="Total Quantity">{{
                    formatQuantity(request.totalQuantity, 
                        request.baseUom)}}</Cell>
                <Cell label="Status">{{request.status}}</Cell>
                <Cell label="Reason">{{request.reason}}</Cell>
                <Cell label="Date Created">{{request.dateCreated}}</Cell>
            </Row>
        </Table>
        <TablePaginator class="w-full justify-end"
            :limit="requests.listLimit" :count="requests.count"
            @change-limit="(limit)=> requests.listLimit = limit"
            @change-page="({limit, offset})=> 
                listStockRequests(limit, offset)" />
    </Section>
</template>

<script>
import Section from '@/components/Section.vue'
import Table from '@/components/Table.vue'
import Row from '@/components/Row.vue'
import Cell from '@/components/Cell.vue'
import TablePaginator from '@/components/TablePaginator.vue'
import Href from '@/components/Href.vue'

import {reactive, watch, onBeforeMount} from 'vue'
import {ItemApi} from '@/utils/apis.js'
import {formatQuantity, reference} from '@/utils/format.js'

export default {
    components: {
        Section, Table, Row, Cell, TablePaginator, Href
    },
    props: {
        data: Object
    },
    setup(props) {
        const requests = reactive({
            list: [],
            listLimit: 5,
            count: 0,
            isProcessing: false,
        })
        const listStockRequests = async (limit, offset)=> {
            requests.isProcessing = true;
            if (props.data && props.data.itemId) {
                const id = props.data.itemId;
                const response = await ItemApi.listItemRequestGroups(id, limit, offset);
                if (response && response.results) {
                    requests.count = response.count;
                    requests.list = response.results.map( requestGroup => ({
                        id: requestGroup.id,
                        totalQuantity: requestGroup.item_requests
                            .filter(i => i.item_id == id)
                            .reduce((a, b)=> a + (b['quantity_needed'] || 0), 0),
                        baseUom: requestGroup.item_requests[0].item_base_uom,
                        reason: requestGroup.reason,
                        status: requestGroup.status,
                        itemRequests: requestGroup.item_requests
                            .filter(i => i.item_id == id)
                            .map( request => ({
                                status: request.status,
                                createdAt: request.created
                            })),
                        dateCreated: requestGroup.created_at 
                    }));
                }
            }
            requests.isProcessing = false;
        }
        onBeforeMount(()=> {
            listStockRequests(requests.listLimit, 0);
        })
        watch(()=> props.data.availableQuantity, ()=> {
            listStockRequests(requests.listLimit, 0);
        })

        return {
            requests, listStockRequests,
            reference,
            formatQuantity: (quantity, unit)=> {
                if (quantity != null && unit != null)
                    return formatQuantity(quantity, unit.abbrev, unit.plural_abbrev)
                else return ''
            },
        }
    }
}
</script>