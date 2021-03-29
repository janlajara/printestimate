<template>
    <div>
        <Section>
            <Table 
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
                            {{stock.availableQty == 1 ? onhand.units.base.name : onhand.units.base.plural}}
                        </span>
                    </Cell>
                    <Cell label="Date Deposited">  
                        {{stock.createdAt}}
                    </Cell>
                    <Cell label="Withdraw Qty">
                        <input type="checkbox" class="input-checkbox" 
                            :value="stock.id" v-model="onhand.withdraw"/> 
                        <input v-if="onhand.withdraw.includes(stock.id)"
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
    </div>
</template>

<script>
import Section from '@/components/Section.vue'
import Table from '@/components/Table.vue'
import Row from '@/components/Row.vue'
import Cell from '@/components/Cell.vue'
import TablePaginator from '@/components/TablePaginator.vue'

import {reactive, watch, inject, computed, onBeforeMount} from 'vue';
import {formatMoney} from '@/utils/format.js';
import {ItemApi} from '@/utils/apis.js';

export default {
    components: {
        Section, Table, Row, Cell, TablePaginator
    },
    props: {
        data: {
            type: Object,
            required: true
        }
    },
    emits: ['withdraw'],
    setup(props, {emit}) {
        const currency = inject('currency');
        const onhand = reactive({
            units: {
                base: {name: null, plural: null},
                alternate: {name: null, plural: null}
            },
            withdraw: [],
            withdrawMap: computed(()=> {
                let withdrawMap = [];
                onhand.withdraw.forEach( stockId => {
                    const stock = onhand.stocks.find(stock => stockId == stock.id)
                    if (stock) withdrawMap.push(
                        {id: stockId, 
                         brandName: stock.brandName,
                         price: stock.price,
                         quantity: parseInt(stock.withdrawQty)})
                })
                return withdrawMap;
            }),
            stocks: [{}],
            stocksLimit: 5,
            stocksCount: 0,
        });
        watch(()=> props.data.units, ()=> {
            if (props.data.units.base) onhand.units.base = props.data.units.base
            if (props.data.units.alternate) onhand.units.alternate = props.data.units.alternate
        })
        watch(()=> props.data.onhandQty, ()=> {
            if (props.data.onhandQty) loadItemStockList(props.data.itemId, onhand.stocksLimit, 0);
        })
        watch(()=> onhand.withdrawMap, ()=> {
            emit('withdraw', Array.from(onhand.withdrawMap))
        })

        const loadItemStockList = async (id, limit, offset) => {
            const response = await ItemApi.getItemStockList(id, limit, offset);
            if (response && response.results) {
                onhand.stocksCount = response.count;
                onhand.stocks = response.results.map(stock => ({
                    id: stock.id, brandName: stock.brand_name,
                    price: stock.price, pricePerQty: stock.price_per_quantity,
                    unbounded: stock.unbounded, baseQty: stock.base_quantity,
                    onhandQty: stock.onhand_quantity, availableQty: stock.available_quantity,
                    createdAt: stock.created_at,
                    withdrawQty: stock.available_quantity
                }));
            }
        }
        onBeforeMount(()=> {
            loadItemStockList(props.data.itemId, onhand.stocksLimit, 0);
        });
        return {
            onhand, loadItemStockList, formatMoney, currency, 
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