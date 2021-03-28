<template>
    <div>
        <Section>
            <Table 
                :headers="['', 'Brand Name', `Price Per ${onhand.units.base.name}`, 
                    'On-hand', 'Available', 'Date Deposited']">
                <Row v-for="(stock, key) in onhand.stocks" :key="key">
                    <Cell>
                        <input type="checkbox" class="input-checkbox" 
                            @change="()=> $emit('withdraw', onhand.withdraw)"
                            :value="stock.id" v-model="onhand.withdraw"/> 
                    </Cell>
                    <Cell label="Brand Name">  
                        {{stock.brandName}}
                    </Cell>
                    <Cell :label="`Price Per ${onhand.units.base.name}`">  
                        {{stock.pricePerQty ? 
                            formatMoney(stock.pricePerQty, currency.abbreviation) : ''}}
                    </Cell>
                    <Cell label="On-hand">  
                        <span v-if="stock.onhandQty">
                            {{stock.onhandQty}} / 
                            {{stock.unbounded ? '∞' : stock.baseQty}} 
                            {{stock.onhandQty == 1 ? onhand.units.base.name : onhand.units.base.plural}}
                        </span>
                    </Cell>
                    <Cell label="Available">  
                        <span v-if="stock.availableQty">
                            {{stock.availableQty}} 
                            {{stock.availableQty == 1 ? onhand.units.base.name : onhand.units.base.plural}}
                        </span>
                    </Cell>
                    <Cell label="Date Deposited">  
                        {{stock.createdAt}}
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

import {reactive, watch, inject, onBeforeMount} from 'vue';
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
    setup(props) {
        const currency = inject('currency');
        const onhand = reactive({
            units: {
                base: {name: null, plural: null},
                alternate: {name: null, plural: null}
            },
            withdraw: [],
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

        const loadItemStockList = async (id, limit, offset) => {
            const response = await ItemApi.getItemStockList(id, limit, offset);
            if (response && response.results) {
                onhand.stocksCount = response.count;
                onhand.stocks = response.results.map(stock => ({
                    id: stock.id, brandName: stock.brand_name,
                    price: stock.price, pricePerQty: stock.price_per_quantity,
                    unbounded: stock.unbounded, baseQty: stock.base_quantity,
                    onhandQty: stock.onhand_quantity, availableQty: stock.available_quantity,
                    createdAt: stock.created_at
                }));
            }
        }
        onBeforeMount(()=> {
            loadItemStockList(props.data.itemId, onhand.stocksLimit, 0);
        });
        return {
            onhand, loadItemStockList, formatMoney, currency
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