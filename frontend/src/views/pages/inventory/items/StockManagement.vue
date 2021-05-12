<template>
    <Section heading="Stock Management">
        <DescriptionList class="grid-cols-2 md:grid-cols-4">
            <DescriptionItem :loader="stock.isProcessing"
                name="Available" :value="stock.data.availableQtyFormatted"/>
            <DescriptionItem :loader="stock.isProcessing"
                name="On-hand" :value="stock.data.onhandQtyFormatted"/>
            <DescriptionItem :loader="stock.isProcessing"
                name="Average Price" :value="stock.data.averagePriceFormatted"/>
            <DescriptionItem :loader="stock.isProcessing"
                name="Latest Price" :value="stock.data.latestPriceFormatted"/>
        </DescriptionList>
        <Tabs>
            <Tab title="Available"> 
                <StocksAvailable
                    @reload="()=> loadItemStockSummary(stock.data.id)"
                    :data="{itemId: stock.data.id, units: $props.data.units}"/>
            </Tab>
            <Tab title="Requests">
                <StockRequests :data="{
                    itemId: stock.data.id, 
                    availableQuantity: stock.data.availableQty}"/>
            </Tab>
            <Tab title="Incoming">
                
            </Tab>
            <!--Tab title="History">
                <StockHistory :data="{
                    itemId: stock.data.id,
                    availableQuantity: stock.data.availableQty}"/>
            </Tab-->
        </Tabs>
    </Section>
</template>

<script>
import Section from '@/components/Section.vue';
import DescriptionList from '@/components/DescriptionList.vue';
import DescriptionItem from '@/components/DescriptionItem.vue';
import Tabs from '@/components/Tabs.vue';
import Tab from '@/components/Tab.vue';
import StocksAvailable from '@/views/pages/inventory/items/StocksAvailable.vue';
import StockRequests from '@/views/pages/inventory/items/StockRequests.vue';
//import StockHistory from '@/views/pages/inventory/stock/StockHistory.vue';

import {reactive, computed, inject, onBeforeMount} from 'vue';
import {ItemApi} from '@/utils/apis.js';
import {formatMoney} from '@/utils/format.js';

export default {
    components: {
        Section, DescriptionList, DescriptionItem, Tabs, Tab,
        StocksAvailable, StockRequests//, StockHistory
    },
    props: {
        data: Object
    },
    setup(props) { 
        const currency = inject('currency')
        const stock = reactive({
            data: {
                id: props.data.itemId,
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
                onhandStocks: []
            },
            isProcessing: false
        });

        const loadItemStockSummary = async (id) => {
            stock.isProcessing = true;
            const response = await ItemApi.retrieveItemStockSummary(id);
            if (response) {
                stock.data.latestPrice = response.latest_price_per_quantity;
                stock.data.averagePrice = response.average_price_per_quantity;
                stock.data.availableQty = response.available_quantity;
                stock.data.availableQtyFormatted = response.available_quantity_formatted;
                stock.data.onhandQty = response.onhand_quantity;
                stock.data.onhandQtyFormatted = response.onhand_quantity_formatted;
            }
            stock.isProcessing = false;
        }
        onBeforeMount(()=> {
            loadItemStockSummary(stock.data.id);
        })

        return {
            stock, loadItemStockSummary
        }
    }
}
</script>