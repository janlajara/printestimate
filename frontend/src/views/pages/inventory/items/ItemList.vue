<template>
    <Page title="Inventory : Items">
        <hr class="my-4"/>
        <ItemInputModal :is-open="item.create.isOpen" :is-create="true" 
            :on-after-save="()=> populateItemList(item.listLimit, 0)"
            @toggle="(value)=> item.create.isOpen = value"/>
        <Section>
            <div class="space-y-4 md:space-y-0 md:flex md:justify-between">
                <div class="my-auto">
                    <Button color="secondary" icon="add"
                        :action="()=>item.create.isOpen = true">
                    Create Item</Button>
                </div>
                <SearchField 
                    placeholder="Search by Item, Brand..." 
                    :disabled="item.isProcessing"
                    @search="(search)=> {
                        populateItemList(item.listLimit, 0, search);
                    }"/>
            </div>
            <Table :loader="item.isProcessing" layout="fixed"
                :headers="['Item', 'Type', 'Price per Unit']"
                :cols-width="['w-2/3', 'w-1/6', 'w-1/6']">
                <Row v-for="(i, key) in item.list" :key="key" clickable
                    @click="()=>goToDetail(i.id)">
                    <Cell label="Item">{{i.name}}</Cell>
                    <Cell label="Type" class="capitalize">{{i.type}}</Cell>
                    <!--Cell label="Available Qty">{{i.availableFormatted}}</Cell>
                    <Cell label="Onhand Qty">{{i.onhandFormatted}}</Cell-->
                    <Cell label="Price per Unit">{{moneyFormat(i.price)}}</Cell>
                </Row>
            </Table>
            <TablePaginator class="w-full justify-end"
                :limit="item.listLimit" :count="item.listCount"
                @change-limit="(limit)=> item.listLimit = limit"
                @change-page="({limit, offset})=> 
                    populateItemList(limit, offset)" />
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
import ItemInputModal from '@/views/pages/inventory/items/ItemInputModal.vue';

import {reactive, onBeforeMount, inject} from 'vue';
import {useRouter} from 'vue-router';
import {ItemApi} from '@/utils/apis.js';
import {formatMoney} from '@/utils/format.js';
import {orderBy} from 'lodash';

export default {
    name: 'Stocks',
    components: {
        Page, Section, Button, SearchField, Table, Row, Cell,
        ItemInputModal, TablePaginator
    },
    setup() {
        const router = useRouter();
        const currency = inject('currency').abbreviation
        const item = reactive({
            create: {
                isOpen: false, 
            },
            isProcessing: false,
            list: [],
            listLimit: 10,
            listCount: 0
        });
        
        const populateItemList = async(limit, offset, search=null) => {
            item.isProcessing = true;
            const response = await ItemApi.listItems(limit, offset, search);
            if (response && response.results) {
                item.listCount = response.count;
                const items = response.results.map(i=> ({
                    id: i.id, name: i.full_name, type: i.type,
                    baseUom: i.base_uom, 
                    available: i.available_quantity,
                    availableFormatted: i.available_quantity_formatted,
                    onhand: i.onhand_quantity,
                    onhandFormatted: i.onhand_quantity_formatted,
                    price: i.price
                }));
                const sorted = orderBy(items, ['name'], ['asc']);
                item.list = sorted;
            }
            item.isProcessing = false;
        }
        onBeforeMount(()=> {
            populateItemList(item.listLimit, 0);
        });

        const moneyFormat = (amount) => 
            amount != null ? formatMoney(amount, currency) : '';
        const goToDetail = (id) => {
            router.push({
                name: 'inventory-item-detail',
                params: {id}});
        }

        return {
            item, populateItemList, moneyFormat, goToDetail
        }
    }
}
</script>