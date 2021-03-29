<template>
    <Section heading="Stock Management" class="mt-12">
        <DescriptionList class="grid-cols-2 md:grid-cols-4">
            <DescriptionItem name="Available" :value="stock.data.availableQtyFormatted"/>
            <DescriptionItem name="On-hand" :value="stock.data.onhandQtyFormatted"/>
            <DescriptionItem name="Average Price" :value="stock.data.averagePriceFormatted"/>
            <DescriptionItem name="Latest Price" :value="stock.data.latestPriceFormatted"/>
        </DescriptionList>
        <Tabs>
            <Tab title="On-hand">
                <div class="flex">
                    <Button icon="add" color="tertiary" class="mr-4"
                        :action="()=> stock.deposit.toggle(true)">Deposit</Button>
                    <StockDepositModal :is-open="stock.deposit.isOpen"
                        :data="{
                            itemId: $props.itemId,
                            units: {
                                base: stock.data.baseUom,
                                alternate: stock.data.altUom}}"
                        @toggle="stock.deposit.toggle"
                        :on-after-deposit="()=>loadItemStocks($props.itemId)"/>
                    <Button icon="remove" class="mr-4" color="secondary"
                        :disabled="!stock.withdraw.hasWithdraw"
                        :action="()=> stock.withdraw.toggle(true)">Withdraw</Button>
                    <div v-if="stock.withdraw.hasWithdraw" class="text-sm my-auto">
                        Selected : <span class="font-bold">{{formatQuantity(stock.withdraw.totalQuantity, 
                            stock.data.baseUom.name, stock.data.baseUom.plural)}}</span>
                    </div>
                </div>
                <StocksOnhand 
                    @withdraw="(selected) => stock.withdraw.selected = selected"
                    :data="{
                        itemId: $props.itemId,
                        onhandQty: stock.data.onhandQty,
                        units: {
                            base: stock.data.baseUom,
                            alternate: stock.data.altUom}}"/>
            </Tab>
            <Tab title="Requests"></Tab>
            <Tab title="Incoming"></Tab>
            <Tab title="History"></Tab>
        </Tabs>
    </Section>
</template>

<script>
import Section from '@/components/Section.vue';
import DescriptionList from '@/components/DescriptionList.vue';
import DescriptionItem from '@/components/DescriptionItem.vue';
import Button from '@/components/Button.vue';
import Tabs from '@/components/Tabs.vue';
import Tab from '@/components/Tab.vue';
import StockDepositModal from '@/views/pages/inventory/stock/StockDepositModal.vue';
import StocksOnhand from '@/views/pages/inventory/stock/StocksOnhand.vue';

import {reactive, computed, inject, onBeforeMount} from 'vue';
import {ItemApi} from '@/utils/apis.js';
import {formatMoney, formatQuantity} from '@/utils/format.js';

export default {
    components: {
        Section, DescriptionList, DescriptionItem, Tabs, Tab, Button,
        StockDepositModal, StocksOnhand
    },
    props: {
        itemId: {
            type: Number,
            required: true
        }
    },
    setup(props) { 
        const currency = inject('currency')
        const stock = reactive({
            data: {
                latestPrice: null, 
                latestPriceFormatted: computed(()=>(
                    stock.data.latestPrice ? 
                        formatMoney(stock.data.latestPrice, currency.abbreviation): null
                )),
                averagePrice: null,
                averagePriceFormatted: computed(()=> (
                    stock.data.averagePrice ?  
                        formatMoney(stock.data.averagePrice, currency.abbreviation): null
                )),
                availableQty: null,
                availableQtyFormatted: null,
                onhandQty: null,
                onhandQtyFormatted: null,
                baseUom: null,
                altUom: null,
                onhandStocks: []
            },
            withdraw: {
                isOpen: false,
                selected: [],
                hasWithdraw: computed(()=> stock.withdraw.selected.length > 0),
                totalQuantity: computed(()=> (
                    stock.withdraw.selected.reduce((a, b)=> a + (b['quantity'] || 0), 0)
                )),
                toggle: (value)=> {
                    stock.withdraw.isOpen = value
                    console.log(stock.withdraw.selected)
                },
            },
            deposit: {
                isOpen: false,
                toggle: (value)=> stock.deposit.isOpen = value,
            }
        });

        const loadItemStocks = async (id) => {
            const response = await ItemApi.retrieveItemStockSummary(id);
            if (response) {
                stock.data.latestPrice = response.latest_price_per_quantity;
                stock.data.averagePrice = response.average_price_per_quantity;
                stock.data.availableQty = response.available_quantity;
                stock.data.availableQtyFormatted = response.available_quantity_formatted;
                stock.data.onhandQty = response.onhand_quantity;
                stock.data.onhandQtyFormatted = response.onhand_quantity_formatted;
                stock.data.baseUom = {
                    value: response.base_uom.id,
                    name: response.base_uom.name,
                    plural: response.base_uom.plural_name};
                stock.data.altUom = {
                    value: (response.alternate_uom)? response.alternate_uom.id: null,
                    name: (response.alternate_uom)? response.alternate_uom.name: null,
                    plural: (response.alternate_uom)? response.alternate_uom.plural_name : null};
            }
        }
        onBeforeMount(()=> {
            loadItemStocks(props.itemId);
        })

        return {
            stock, loadItemStocks, formatQuantity
        }
    }
}
</script>