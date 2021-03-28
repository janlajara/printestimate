<template>
    <Page :title="(item.detail.isOpen)? item.detail.selectedItem : 'Inventory : Stock'">
        <hr class="my-4"/>
        <ItemInputModal :is-open="item.create.isOpen" :is-create="true" 
            :on-after-save="()=> populateItemList(item.listLimit, 0)"
            @toggle="(value)=> item.create.isOpen = value"/>
        <Section>
            <div v-if="item.detail.isOpen"> 
                <ItemDetail :item-id="item.detail.id" :key="item.detail.key"
                    :is-open="item.detail.isOpen" 
                    :on-after-delete="()=> populateItemList(item.listLimit, 0)"
                    @toggle="(value)=> item.detail.isOpen = value"/>
            </div>
            <div v-else>
                <Button color="secondary" :action="()=>item.create.isOpen = true">
                    Create Item</Button>
                <Table :headers="['Item', 'Type', 'Unit of Measure', 
                    'Available Qty', 'On-hand Qty']">
                    <Row v-for="(i, key) in item.list" :key="key"
                        :select="()=>item.detail.open(i.id, i.name)">
                        <Cell label="Item">{{i.name}}</Cell>
                        <Cell label="Type" class="capitalize">{{i.type}}</Cell>
                        <Cell label="UoM">{{i.baseUom}}</Cell>
                        <Cell label="Available Qty">{{i.available}}</Cell>
                        <Cell label="Onhand Qty">{{i.onhand}}</Cell>
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
import Table from '@/components/Table.vue';
import Row from '@/components/Row.vue';
import Cell from '@/components/Cell.vue';
import TablePaginator from '@/components/TablePaginator.vue';
import ItemInputModal from '@/views/pages/inventory/stock/ItemInputModal.vue';
import ItemDetail from '@/views/pages/inventory/stock/ItemDetail.vue';

import {reactive, onBeforeMount} from 'vue';
import {ItemApi} from '@/utils/apis.js';

export default {
    name: 'Stock',
    components: {
        Page, Section, Button, Table, Row, Cell,
        ItemInputModal, ItemDetail, TablePaginator
    },
    setup() {
        const item = reactive({
            create: {
                isOpen: false, 
            },
            detail: {
                id: null,
                isOpen: false,
                selectedItem: null,
                open: async (id, name)=> { 
                    item.detail.isOpen = true;
                    item.detail.id = id;
                    item.detail.selectedItem = name;
                },
                close: ()=> {
                    item.detail.isOpen = false;
                    item.detail.id = null;
                },
            },
            list: [{}],
            listLimit: 5,
            listCount: 0
        });
        
        const populateItemList = async(limit, offset) => {
            const response = await ItemApi.listItems(limit, offset);
            if (response && response.results) {
                item.listCount = response.count;
                item.list = response.results.map(i=> ({
                    id: i.id, name: i.full_name, type: i.type,
                    baseUom: i.base_uom, 
                    available: i.available_quantity,
                    onhand: i.onhand_quantity 
                }))
            }
        }
        onBeforeMount(()=> {
            populateItemList(item.listLimit, 0);
        });

        return {
            item, populateItemList
        }
    }
}
</script>