<template>
    <Page :title="(item.detail.isOpen)? item.detail.selectedItem : 'Inventory : Stock'">
        <hr class="my-4"/>
        <ItemInputModal :is-open="item.create.isOpen" :is-create="true" 
            :on-after-save="populateItemList"
            @toggle="(value)=> item.create.isOpen = value"/>
        <Section>
            <div v-if="item.detail.isOpen"> 
                <ItemDetail :item-id="item.detail.id" :key="item.detail.key"
                    :is-open="item.detail.isOpen" 
                    :on-after-delete="populateItemList"
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
import ItemInputModal from '@/views/pages/inventory/stock/ItemInputModal.vue';
import ItemDetail from '@/views/pages/inventory/stock/ItemDetail.vue';

import {reactive} from 'vue';
import {ItemApi} from '@/utils/apis.js';

export default {
    name: 'Stock',
    components: {
        Page, Section, Button, Table, Row, Cell, ItemInputModal, ItemDetail
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
            list: [{}]
        });
        
        const populateItemList = async() => {
            const response = await ItemApi.listItems();
            item.list = response.map(i=> ({
                id: i.id, name: i.full_name, type: i.type,
                baseUom: i.base_uom, 
                available: i.available_quantity,
                onhand: i.onhand_quantity 
            }))
        }
        populateItemList();

        return {
            item, populateItemList
        }
    }
}
</script>