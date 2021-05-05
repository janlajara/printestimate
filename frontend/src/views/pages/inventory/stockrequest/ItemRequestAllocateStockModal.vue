<template> 
    <Modal :heading="detail.data.itemName" :is-open="$props.isOpen"
        @toggle="(value)=> $emit('toggle', value)">
        <!--Section heading="Details" class="grid md:grid-cols-4 md:gap-4">
            <DescriptionList class="md:grid-cols-2 md:col-span-3">
                <DescriptionItem :loader="detail.isProcessing"
                    name="Item Name" :value="detail.data.itemName"/>
                <DescriptionItem :loader="detail.isProcessing" 
                    name="Status" :value="detail.data.status"/>
                <DescriptionItem :loader="detail.isProcessing"
                    name="Quantity Needed" 
                    :value="detail.data.quantityNeeded"/>
                <DescriptionItem :loader="detail.isProcessing"
                    name="Date Created" :value="detail.data.dateCreated"/>
            </DescriptionList>
        </Section>
        <hr class="pb-2"/-->
        <Section heading="Allocated Stocks" class="grid md:grid-cols-4 md:gap-4">
            <div class="mt-3 md:grid-cols-2 md:col-span-3">
                <p>Request has a total of 
                    <span class="font-bold">{{detail.data.quantityStocked}}</span> 
                    allocated.</p>
                <div class="bg-tertiary-light bg-opacity-70 rounded">
                    <Table :headers="['Stock Id', 'Brand Name', 'Quantity', '']">
                        <Row v-for="(sr, i) in detail.data.stockRequests" :key="i"
                            :class="sr.fulfilled ? 'text-gray-400' : ''">
                            <Cell label="Stock Id">{{sr.stockCode}}</Cell>
                            <Cell label="Brand Name">{{sr.stockName}}</Cell>
                            <Cell label="Quantity">{{sr.quantityFormatted}}</Cell>
                            <Cell class="flex justify-end flex-grow">
                                <span v-if="sr.fulfilled" 
                                    class="inline-block align-middle material-icons 
                                        text-xs text-secondary">
                                    check</span>
                                <button v-else
                                    :disabled="$props.readOnly || detail.isProcessing"
                                    @click="()=>deleteStockRequest(sr.id)"
                                    class="material-icons text-sm"
                                    :class="$props.readOnly || detail.isProcessing ? 
                                        'text-gray-400' : 'hover:text-secondary text-black'">
                                    delete</button>
                            </Cell>
                        </Row>
                    </Table>   
                    <div class="w-full flex space-y-2 flex-col sm:space-y-0 sm:space-x-2 
                        sm:flex-row flex-wrap p-4 -mt-4">
                        <InputTextLookup class="flex-grow"
                            @select="selected => {
                                detail.form.stock.select(selected)
                            }"
                            @input="search => {
                                detail.form.stock.search = search;
                                detail.form.stock.selected.id = null;
                                lookupStock(search);
                            }"
                            :options="detail.form.stock.options.map( option => ({
                                value: option.id,
                                title: option.brandName,
                                subtitle: option.code,
                                figure: option.availableQuantityFormatted,
                                timestamp: option.createdAt
                            }))"
                            :value="detail.form.stock.search"
                            :disabled="detail.form.readOnly"
                            placeholder="Search Stock" 
                            bg="white" size="small"/>
                        <input type="text" v-number 
                            @input="event => {
                                detail.form.stock.quantity = event.target.value;
                            }"
                            :value="detail.form.stock.quantity"
                            :disabled="detail.form.readOnly"
                            :min="Math.min(detail.data.missingAllocation, 1)" 
                            :max="detail.form.stock.selected.quantity != null ? 
                                Math.min(detail.form.stock.selected.quantity, 
                                    detail.data.missingAllocation) : 
                                detail.data.missingAllocation"
                            class="text-xs border-0 rounded sm:w-28"
                            :placeholder="`${detail.data.itemUom.name} Quantity`"/>
                        <div class="flex justify-end">
                            <Button icon="add" 
                                @click="detail.form.stock.add"
                                :disabled="detail.form.readOnly">
                                Add
                            </Button>
                        </div>
                    </div>
                </div>
            </div>
        </Section>
    </Modal>
</template>

<script>
import Modal from '@/components/Modal.vue';
import Section from '@/components/Section.vue';
//import DescriptionList from '@/components/DescriptionList.vue';
//import DescriptionItem from '@/components/DescriptionItem.vue';
import Table from '@/components/Table.vue';
import Row from '@/components/Row.vue';
import Cell from '@/components/Cell.vue';
import Button from '@/components/Button.vue';
import InputTextLookup from '@/components/InputTextLookup.vue';

import {reactive, computed, watch, onBeforeMount} from 'vue';
import {ItemApi, ItemRequestApi, StockRequestApi} from '@/utils/apis.js'
import {formatQuantity, reference} from '@/utils/format.js'

export default {
    components: {
        Modal, Section, //DescriptionList, DescriptionItem,
        Table, Row, Cell, Button, InputTextLookup,
    },
    emits: ['toggle'],
    props: {
        isOpen: Boolean,
        itemRequestId: Number,
        readOnly: Boolean
    },
    setup(props) {
        const detail = reactive({
            id: props.itemRequestId,
            data: {
                itemId: null,
                itemName: '',
                itemUom: {plural_abbrev: ''},
                statusChoices: []
            },
            form: {
                readOnly: computed(()=> {
                    return (detail.data.isFullyAllocated || 
                        detail.isProcessing) || props.readOnly
                }),
                stock: {
                    options: [],
                    selected: {
                        id: null,
                        quantity: computed(()=> {
                            const stockId = detail.form.stock.selected.id;
                            let quantity = null;
                            if (stockId != null) {
                                const stock = detail.form.stock.options.find(
                                    option => option.id == stockId);
                                quantity = stock.availableQuantity;
                            }
                            return quantity;
                        })
                    },
                    search: null,
                    quantity: null,
                    select: (stockId)=> {
                        detail.form.stock.selected.id = stockId;
                        if (detail.data.missingAllocation > 0 && 
                            detail.form.stock.selected.quantity != null) {
                            detail.form.stock.quantity = Math.min(
                                detail.form.stock.selected.quantity,
                                detail.data.missingAllocation)
                        }
                    },
                    add: async ()=> {
                        if (detail.form.stock.search == null || 
                            detail.form.stock.search == null)
                            return;

                        detail.isProcessing = true;
                        const itemId = detail.data.itemId;

                        if (detail.id && detail.form.stock.selected.id && itemId) {
                            const request = {
                                item_request_id: detail.id,
                                stock_requests: [{
                                    id: detail.form.stock.selected.id,
                                    quantity: detail.form.stock.quantity
                                }]
                            }
                            const response = await ItemApi.requestStocks(itemId, request);
                            if (response && !response.error) {
                                retrieveItemRequest();
                                detail.form.stock.search = null;
                                detail.form.stock.quantity = null;
                                detail.form.stock.selected.id = null;
                            }
                        }
                        detail.isProcessing = false;
                    }
                },
            },
            isProcessing: false,
        })
        const lookupStock = async (search)=> {
            if (detail.data.itemId) { 
                const response = await ItemApi.listItemStocks(
                    detail.data.itemId, 5, 0, true, search)
                if (response && response.results) {
                    detail.form.stock.options = response.results.map(stock => ({
                        id: stock.id,
                        code: reference.formatId(stock.id, reference.stock),
                        brandName: stock.brand_name,
                        availableQuantity: stock.available_quantity,
                        availableQuantityFormatted: stock.available_quantity_formatted,
                        createdAt: stock.created_at
                    }));
                } else {
                    detail.form.stock.options = []
                }
            }
        }
        const deleteStockRequest = async (srId)=> {
            detail.isProcessing = true;
            if (srId) {
                await StockRequestApi.deleteStockRequest(srId);
                retrieveItemRequest();
            }
            detail.isProcessing = false;
        }
        const retrieveItemRequest = async ()=> {
            detail.isProcessing = true; 
            if (detail.id) {
                const response = await ItemRequestApi.retrieveItemRequest(detail.id);
                detail.data = {
                    itemId: response.item_id,
                    itemName: response.item_name,
                    itemUom: response.item_base_uom,
                    status: response.status,
                    statusChoices: response.status_choices,
                    quantityNeeded: response.quantity_needed_formatted,
                    quantityStocked: response.quantity_stocked_formatted, 
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
        watch(()=> props.isOpen, ()=> {
            detail.id = props.itemRequestId;
            retrieveItemRequest();
        });
        onBeforeMount(retrieveItemRequest);

        return {
            detail, lookupStock,
            deleteStockRequest,
            formatQuantity: (quantity, unit) => {
                formatQuantity(quantity, unit.abbrev, unit.plural_abbrev)}
        }
    }
}
</script>