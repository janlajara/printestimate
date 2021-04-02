<template>
    <Section>
        <Table :loader="history.isProcessing"
            :headers="['Action', 'Brand', 'Price per Unit', 'Quantity', 'Timestamp']">
            <Row v-for="(log, key) in history.list" :key="key">
                <Cell label="Action">{{log.action}}</Cell>
                <Cell label="Brand">{{log.brandName}}</Cell>
                <Cell label="Price per Unit">
                    {{formatMoney(log.pricePerUnit)}}</Cell>
                <Cell label="Quantity">
                    {{formatQuantity(log.quantity, log.baseUom)}}</Cell>
                <Cell label="Timestamp">{{log.createdAt}}</Cell>
            </Row>
        </Table>
        <TablePaginator class="w-full justify-end"
            :limit="history.listLimit" :count="history.count"
            @change-limit="(limit)=> history.listLimit = limit"
            @change-page="({limit, offset})=> 
                listStockHistory(limit, offset)" />
    </Section>
</template>

<script>
import Section from '@/components/Section.vue'
import Table from '@/components/Table.vue'
import Row from '@/components/Row.vue'
import Cell from '@/components/Cell.vue'
import TablePaginator from '@/components/TablePaginator.vue'

import {reactive, onBeforeMount, inject, watch} from 'vue'
import {ItemApi} from '@/utils/apis.js'
import {formatQuantity, formatMoney} from '@/utils/format.js'

export default {
    components: {
        Section, Table, Row, Cell, TablePaginator
    },
    props: {
        data: Object
    },
    setup(props) {
        const currency = inject('currency').abbreviation
        const history = reactive({
            list: [],
            listLimit: 5,
            count: 0,
            isProcessing: false,
        });
        const listStockHistory = async (limit, offset)=> {
            history.isProcessing = true; 
            if (props.data && props.data.itemId) {
                const response = await ItemApi.listItemStockHistory(
                    props.data.itemId, limit, offset); 
                if (response && response.results) {
                    history.count = response.count
                    history.list = response.results.map(log => ({
                        brandName: log.stock.brand_name,
                        pricePerUnit: log.stock.price_per_quantity,
                        baseUom: log.stock.base_uom,
                        alternateUom: log.stock.alternate_uom,
                        quantity: log.stock_unit.quantity,
                        action: log.action,
                        createdAt: log.created
                    }))
                }
            }
            history.isProcessing = false;
        }
        onBeforeMount(()=> {
            listStockHistory(history.listLimit, 0);
        });
        watch(()=> props.data.availableQuantity, ()=> {
            listStockHistory(history.listLimit, 0);
        })
        return {
            history, listStockHistory,
            formatQuantity: (quantity, unit)=> {
                if (quantity != null && unit != null)
                    return formatQuantity(quantity, unit.abbrev, unit.plural_abbrev)
                else return ''
            },
            formatMoney: (amount)=> {
                if (amount != null)
                    return formatMoney(amount, currency)
                else return ''
            }
        }
    }
}
</script>