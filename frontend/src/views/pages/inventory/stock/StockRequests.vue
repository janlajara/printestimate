<template>
    <Section>
        <Table :loader="requests.isProcessing"
            :headers="['Request #', 'Total Quantity', 'Status', 'Reason', 'Date Created']">
            <Row v-for="(request, key) in requests.list" :key="key">
                <Cell label="Request #">{{
                    reference.formatId(request.id, reference.stockRequest)}}</Cell>
                <Cell label="Total Quantity">{{
                    formatQuantity(request.totalQuantity, 
                        request.stockRequests[0].baseUom)}}</Cell>
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

import {reactive, onBeforeMount} from 'vue'
import {ItemApi} from '@/utils/apis.js'
import {formatQuantity, reference} from '@/utils/format.js'

export default {
    components: {
        Section, Table, Row, Cell, TablePaginator
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
                const response = await ItemApi.listItemStockRequests(id, limit, offset);
                if (response && response.results) {
                    requests.count = response.count;
                    requests.list = response.results.map( requestGroup => ({
                        id: requestGroup.id,
                        totalQuantity: requestGroup.stock_requests
                            .reduce((a, b)=> a + (b['stock_unit']['quantity'] || 0), 0),
                        reason: requestGroup.reason,
                        status: requestGroup.status,
                        stockRequests: requestGroup.stock_requests.map( request => ({
                            brandName: request.stock.brand_name,
                            status: request.status,
                            price: request.stock.price_per_quantity,
                            baseUom: request.stock.base_uom,
                            alternateUom: request.stock.alternate_uom,
                            withdrawQuantity: request.stock_unit.quantity,
                            baseQuantity: request.stock.base_quantity,
                            baseQuantityFormatted: request.stock.base_quantity_formatted,
                            onhandQuantity: request.stock.onhand_quantity,
                            onhandQuantityFormatted: request.stock.onhand_quantity_formatted,
                            availableQuantity: request.stock.available_quantity,
                            availableQuantityFormatted: request.stock.available_quantity_formatted,
                            createdAt: request.created,
                            lastModified: request.last_modified
                        })),
                        dateCreated: requestGroup.created_at 
                    }));
                    console.log(requests.list)
                }
            }
            requests.isProcessing = false;
        }
        onBeforeMount(()=> {
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