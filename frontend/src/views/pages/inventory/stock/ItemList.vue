<template>
    <Page :title="(item.detail.isOpen)? item.detail.selectedItem : 'Inventory : Stocks'">
        <hr class="my-4"/>
        <ItemInputModal :is-open="item.create.isOpen" :is-create="true" 
            :on-after-save="()=> populateItemList(item.listLimit, 0)"
            @toggle="(value)=> item.create.isOpen = value"/>
        <Section>
            <div v-if="item.detail.isOpen"> 
                <ItemDetail :item-id="item.detail.id" :key="item.detail.key"
                    :is-open="item.detail.isOpen" 
                    @toggle="(value)=> {
                        item.detail.isOpen = value;
                        if (!value) populateItemList(item.listLimit, 0);
                    }"/>
            </div>
            <div v-else>
                <div class="space-y-4 md:space-y-0 md:flex md:justify-between">
                    <div class="my-auto">
                        <Button color="secondary" icon="add"
                            :action="()=>item.create.isOpen = true">
                        Create Item</Button>
                    </div>
                    <SearchField placeholder="Search" :disabled="item.isProcessing"
                        @search="(search)=> {
                            populateItemList(item.listLimit, 0, search);
                        }"/>
                </div>
                <Table :headers="['Item', 'Type', 'Available Qty', 
                        'On-hand Qty', 'Price per Unit']"
                        :loader="item.isProcessing">
                    <Row v-for="(i, key) in item.list" :key="key" clickable
                        @click="()=>item.detail.open(i.id, i.name)">
                        <Cell label="Item">{{i.name}}</Cell>
                        <Cell label="Type" class="capitalize">{{i.type}}</Cell>
                        <Cell label="Available Qty">{{i.availableFormatted}}</Cell>
                        <Cell label="Onhand Qty">{{i.onhandFormatted}}</Cell>
                        <Cell label="Price per Unit">{{moneyFormat(i.price)}}</Cell>
                    </Row>
                </Table>
                <TablePaginator class="w-full justify-end"
                    :limit="item.listLimit" :count="item.listCount"
                    @change-limit="(limit)=> item.listLimit = limit"
                    @change-page="({limit, offset})=> 
                        populateItemList(limit, offset)" />
            </div>
        </Section>
    </Page>
</template>

<script>
import Page from '@/components/Page.vue';
import Section from '@/components/Section.vue';
import Button from '@/components/Button.vue' ;
import SearchField from '@/components/SearchField.vue';
import Table from '@/components/Table.vue';
import Row from '@/components/Row.vue';
import Cell from '@/components/Cell.vue';
import TablePaginator from '@/components/TablePaginator.vue';
import ItemInputModal from '@/views/pages/inventory/stock/ItemInputModal.vue';
import ItemDetail from '@/views/pages/inventory/stock/ItemDetail.vue';

import {reactive, onBeforeMount, inject} from 'vue';
import {ItemApi} from '@/utils/apis.js';
import {formatMoney} from '@/utils/format.js'

export default {
    name: 'Stocks',
    components: {
        Page, Section, Button, SearchField, Table, Row, Cell,
        ItemInputModal, ItemDetail, TablePaginator
    },
    setup() {
        const currency = inject('currency').abbreviation
        const item = reactive({
            create: {
                isOpen: false, 
            },
            detail: {
                id: null,
                isOpen: false,
                selectedItem: null,
                open: async (id, name)=> { 
                    if (id) {
                        item.detail.isOpen = true;
                        item.detail.id = id;
                        item.detail.selectedItem = name;
                    }
                },
                close: ()=> {
                    item.detail.isOpen = false;
                    item.detail.id = null;
                },
            },
            isProcessing: false,
            list: [{}],
            listLimit: 5,
            listCount: 0
        });
        
        const populateItemList = async(limit, offset, search=null) => {
            item.isProcessing = true;
            const response = await ItemApi.listItems(limit, offset, search);
            if (response && response.results) {
                item.listCount = response.count;
                item.list = response.results.map(i=> ({
                    id: i.id, name: i.full_name, type: i.type,
                    baseUom: i.base_uom, 
                    available: i.available_quantity,
                    availableFormatted: i.available_quantity_formatted,
                    onhand: i.onhand_quantity,
                    onhandFormatted: i.onhand_quantity_formatted,
                    price: i.price
                }))
            }
            item.isProcessing = false;
        }
        onBeforeMount(()=> {
            populateItemList(item.listLimit, 0);
        });

        const moneyFormat = (amount) => 
            amount != null ? formatMoney(amount, currency) : '';

        return {
            item, populateItemList, moneyFormat
        }
    }
}
</script>