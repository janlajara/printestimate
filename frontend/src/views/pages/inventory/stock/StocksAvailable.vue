<template>
    <Section>
        <div class="flex">
            <Button icon="download" color="tertiary" 
                class="mr-4" :disabled="onhand.withdraw.hasSelected || onhand.isProcessing"
                :action="()=> onhand.deposit.toggle(true)">Deposit</Button>
            <StockDepositModal :is-open="onhand.deposit.isOpen"
                :data="{
                    itemId: $props.data.itemId,
                    units: {
                        base: onhand.units.base,
                        alternate: onhand.units.alternate}}"
                @toggle="onhand.deposit.toggle"
                :on-after-deposit="()=>{
                    loadItemStockList($props.data.itemId, onhand.stocksLimit, 0);
                    $emit('reload');
            }"/>
            <Button icon="upload" class="mr-4" 
                color="secondary" :disabled="!onhand.withdraw.hasSelected || onhand.isProcessing"
                :action="()=> onhand.withdraw.toggle(true)">Withdraw</Button>
            <div v-if="onhand.withdraw.hasSelected" class="text-sm my-auto">
                Selected : <span class="font-bold">
                    {{onhand.withdraw.totalQuantityFormatted}}</span>
            </div>
            <StockWithdrawModal :is-open="onhand.withdraw.isOpen"
                :data="{
                    itemId: $props.data.itemId,
                    unit: onhand.units.base.name,
                    total: onhand.withdraw.totalQuantityFormatted,
                    selected: onhand.withdraw.map}"
                @toggle="onhand.withdraw.toggle"
                :on-after-withdraw="()=>{
                    loadItemStockList($props.data.itemId, onhand.stocksLimit, 0);
                    $emit('reload');
                    onhand.withdraw.selected = [];
            }"/>
        </div>
        <Table :loader="onhand.isProcessing"
            :headers="['Brand Name', 
                `Price / ${onhand.units.base.name}`, 
                'Available', 'Date Deposited', 'Withdraw Qty']"> 
            <Row v-for="(stock, key) in onhand.stocks" :key="key">
                <Cell label="Brand Name">  
                    {{stock.brandName}}
                </Cell>
                <Cell :label="`Price / ${onhand.units.base.name}`">  
                    {{stock.pricePerQty ? 
                        formatMoney(stock.pricePerQty, currency.abbreviation) : ''}}
                </Cell>
                <Cell label="Available">  
                    <span v-if="stock.availableQty">
                        {{stock.availableQty}} / 
                        {{stock.unbounded ? '∞' : stock.baseQty}} 
                        {{onhand.units.getUnit(stock.availableQty,  onhand.units.base)}}
                    </span>
                </Cell>
                <Cell label="Date Deposited">  
                    {{stock.createdAt}}
                </Cell>
                <Cell label="Withdraw Qty">
                    <input type="checkbox" class="input-checkbox" 
                        :value="stock.id" v-model="onhand.withdraw.selected"/> 
                    <input v-if="onhand.withdraw.selected.includes(stock.id)"
                        :value="stock.withdrawQty"
                        @input="(event)=> inputWithdraw(event, stock)"
                        type="text" class="text-xs rounded p-1 ml-4 w-14 border-tertiary" 
                        style="-moz-appearance:textfield;"/>
                </Cell>
            </Row>
        </Table>
        <TablePaginator class="w-full justify-end"
            :limit="onhand.stocksLimit" :count="onhand.stocksCount"
            @change-limit="(limit)=> onhand.stocksLimit = limit"
            @change-page="({limit, offset})=> 
                loadItemStockList($props.data.itemId, limit, offset)" />
    </Section>
</template>

<script>
import Section from '@/components/Section.vue'
import Table from '@/components/Table.vue'
import Row from '@/components/Row.vue'
import Cell from '@/components/Cell.vue'
import TablePaginator from '@/components/TablePaginator.vue'
import Button from '@/components/Button.vue'
import StockDepositModal from '@/views/pages/inventory/stock/StockDepositModal'
import StockWithdrawModal from '@/views/pages/inventory/stock/StockWithdrawModal'

import {reactive, inject, computed, onBeforeMount} from 'vue';
import {formatMoney, formatQuantity} from '@/utils/format.js';
import {ItemApi} from '@/utils/apis.js';

export default {
    components: {
        Section, Table, Row, Cell, TablePaginator, Button, StockDepositModal, StockWithdrawModal
    },
    props: {
        data: {
            type: Object,
            required: true
        }
    },
    emits: ['reload'],
    setup(props) {
        const currency = inject('currency');
        const onhand = reactive({
            units: {
                base: computed(()=> {
                    const firstStock = onhand.stocks[0]
                    if (firstStock.id) return firstStock.baseUom
                    return {name: null, plural: null}
                }),
                alternate: computed(()=> {
                    const firstStock = onhand.stocks[0]
                    if (firstStock.id) return firstStock.alternateUom
                    return {name: null, plural: null}
                }),
                formatQuantity: (quantity, unit)=> {
                    if (quantity != null)
                        return formatQuantity(quantity, unit.abbrev, unit.plural_abbrev)
                    else return ''
                },
                getUnit: (quantity, unit)=> {
                    return quantity == 1 ? unit.abbrev : unit.plural_abbrev
                }
            },
            isProcessing: false,
            withdraw: {
                isOpen: false,
                selected: [],
                hasSelected: computed(()=> onhand.withdraw.selected.length > 0),
                totalQuantity: computed(()=> (
                    onhand.withdraw.map.reduce((a, b)=> a + (b['quantity'] || 0), 0)
                )),
                totalQuantityFormatted: computed(()=> {
                    const qty = onhand.withdraw.totalQuantity;
                    return onhand.units.formatQuantity(qty, onhand.units.base)
                }),
                map: computed(()=> {
                    let map = [];
                    onhand.withdraw.selected.forEach( stockId => {
                        const stock = onhand.stocks.find(stock => stockId == stock.id)
                        if (stock) map.push(
                            {id: stockId, 
                            brandName: stock.brandName,
                            price: stock.price,
                            quantity: parseInt(stock.withdrawQty),
                            quantityFormatted: 
                                onhand.units.formatQuantity(stock.withdrawQty, onhand.units.base)})
                    })
                    return map;
                }),
                toggle: (value)=> {
                    onhand.withdraw.isOpen = value
                }
            },
            deposit: {
                isOpen: false,
                toggle: (value)=> onhand.deposit.isOpen = value,
            },
            stocks: [{}],
            stocksLimit: 5,
            stocksCount: 0,
        });
        onBeforeMount(()=> {
            loadItemStockList(props.data.itemId, onhand.stocksLimit, 0);
            onhand.withdraw.selected = [];
        })

        const loadItemStockList = async (id, limit, offset) => {
            if (id == null) return;

            onhand.isProcessing = true;
            const response = await ItemApi.listItemStocks(id, limit, offset, true);
            if (response && response.results) {
                onhand.stocksCount = response.count;
                onhand.stocks = response.results
                    .map(stock => ({
                        id: stock.id, brandName: stock.brand_name,
                        price: stock.price, pricePerQty: stock.price_per_quantity,
                        unbounded: stock.unbounded, baseQty: stock.base_quantity,
                        baseUom: stock.base_uom, alternateUom: stock.alternate_uom,
                        onhandQty: stock.onhand_quantity, 
                        onhandQtyFormatted: stock.onhand_quantity_formatted,
                        availableQty: stock.available_quantity,
                        availableQtyFormatted: stock.available_quantity_formatted,
                        createdAt: stock.created_at,
                        withdrawQty: stock.available_quantity
                    }));
            }
            onhand.isProcessing = false;
        }

        return {
            onhand, loadItemStockList, formatMoney, formatQuantity, currency, 
            inputWithdraw: (event, stock)=> {
                const value = event.target.value
                const replaced = value != null ?  
                    value.replace(/[^\d]/g, '') : null;
                let withdrawQty = stock.availableQty;
                if (replaced < 1) {
                    withdrawQty = 1;
                } else if (stock.availableQty >= replaced) {
                    withdrawQty = replaced;
                }  
                event.target.value = withdrawQty;
                stock.withdrawQty = withdrawQty;
            },
        };
    }
}
</script>

<style scoped>
@layer components {
  .input-checkbox {
    @apply border-none rounded bg-gray-300 text-primary;
  }
  .input-checkbox:checked {
    @apply bg-checkbox;
  }
}
</style>