<template>
    <Modal heading="Item Request" :is-open="$props.isOpen"
        @toggle="(value)=> $emit('toggle', value)">
        <Section heading="Details" class="grid md:grid-cols-4 md:gap-4">
            <DescriptionList class="md:grid-cols-2 md:col-span-3">
                <DescriptionItem :loader="detail.isProcessing"
                    name="Item Name" :value="detail.data.itemName"/>
                <DescriptionItem :loader="detail.isProcessing" 
                    name="Status" :value="detail.data.status"/>
                <DescriptionItem :loader="detail.isProcessing"
                    name="Quantity Needed" :value="detail.data.quantityNeeded"/>
                <DescriptionItem :loader="detail.isProcessing"
                    name="Date Created" :value="detail.data.dateCreated"/>
            </DescriptionList>
        </Section>
        <hr/>
        <Section heading="Allocated Stocks" class="grid md:grid-cols-4 md:gap-4">
            <div class="md:col-span-3">
                <Table :headers="['Stock Id', 'Brand Name', 'Quantity', '']">
                    <Row v-for="(sr, i) in detail.data.stockRequests" :key="i">
                        <Cell label="Stock Id">{{sr.stockCode}}</Cell>
                        <Cell label="Brand Name">{{sr.stockName}}</Cell>
                        <Cell label="Quantity">{{sr.quantityFormatted}}</Cell>
                        <Cell></Cell>
                    </Row>
                    <Row>
                        <Cell colspan="4">
                            <div class="flex space-x-2 flex-wrap">
                                <input type="text"
                                    :disabled="detail.data.isFullyAllocated"
                                    class="text-xs border-0 rounded flex-grow"
                                    placeholder="Stock"/>
                                <input type="text"  v-number 
                                    :disabled="detail.data.isFullyAllocated"
                                    :min="Math.min(detail.data.missingAllocation, 1)" 
                                    :max="detail.data.missingAllocation"
                                    class="text-xs border-0 rounded w-28"
                                    :placeholder="`${detail.data.itemUom.name} Quantity`"/>
                                <div>
                                    <Button icon="add" 
                                        :disabled="detail.data.isFullyAllocated">
                                        Add
                                    </Button>
                                </div>
                            </div>
                        </Cell>
                    </Row>
                </Table>             
            </div>
        </Section>
    </Modal>
</template>

<script>
import Modal from '@/components/Modal.vue';
import Section from '@/components/Section.vue';
import DescriptionList from '@/components/DescriptionList.vue';
import DescriptionItem from '@/components/DescriptionItem.vue';
import Table from '@/components/Table.vue';
import Row from '@/components/Row.vue';
import Cell from '@/components/Cell.vue';
import Button from '@/components/Button.vue';

import {reactive, watch, onBeforeMount} from 'vue';
import {ItemRequestApi} from '@/utils/apis.js'
import {formatQuantity, reference} from '@/utils/format.js'

export default {
    components: {
        Modal, Section, DescriptionList, DescriptionItem,
        Table, Row, Cell, Button
    },
    emits: ['toggle'],
    props: {
        isOpen: Boolean,
        itemRequestId: Number
    },
    setup(props) {
        const detail = reactive({
            id: props.itemRequestId,
            data: {
                itemUom: {plural_abbrev: ''},
                statusChoices: []
            },
            form: {
                stock: null,
                quantity: null,
                status: null,
                comments: null,
                addStock: (stockId, quantity) => {
                    console.log(stockId, quantity);
                }
            },
            isProcessing: false,
        })

        const retrieveItemRequest = async ()=> {
            detail.isProcessing = true; 
            if (detail.id) {
                const response = await ItemRequestApi.retrieveItemRequest(detail.id);
                detail.data = {
                    itemName: response.item_name,
                    itemUom: response.item_base_uom,
                    status: response.status,
                    statusChoices: response.status_choices,
                    quantityNeeded: response.quantity_needed_formatted,
                    isFullyAllocated: response.is_fully_allocated,
                    missingAllocation: response.missing_allocation, 
                    dateCreated: response.created,
                    stockRequests: response.stock_requests.map(sr => ({
                        id: sr.id,
                        stockCode: reference.formatId(sr.id, reference.stock),
                        stockName: sr.stock_name,
                        fulfilled: sr.is_fulfilled,
                        quantity: sr.quantity,
                        quantityFormatted: sr.quantity_formatted
                    }))
                }
            }
            detail.isProcessing = false;
        }
        watch(()=> props.itemRequestId, ()=> {
            detail.id = props.itemRequestId;
            retrieveItemRequest();
        });
        onBeforeMount(retrieveItemRequest);

        return {
            detail,
            formatQuantity: (quantity, unit) => {
                formatQuantity(quantity, unit.abbrev, unit.plural_abbrev)}
        }
    }
}
</script>