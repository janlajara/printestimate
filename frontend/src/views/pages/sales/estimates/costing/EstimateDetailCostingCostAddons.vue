<template>
    <div>
        <!-- Table Rows for Services -->
        <div class="text-primary-dark font-bold">
            <span>Cost Add-ons</span>
        </div>

        <div v-for="(addon, w) in state.data.costAddons" :key="w"
            class="border-b">
            <div class="grid grid-cols-2">
                <div>
                    <div class="flex my-auto">
                        <div class="ml-8">
                            <span class="text-sm inline-block align-middle">
                                {{addon.name}}</span>
                        </div>
                        <div class="ml-4 flex-auto text-right">
                            <span class="text-xs inline-block align-middle">
                                {{addon.type == 'flat'?
                                    formatMoney(addon.addonValue):
                                    `${addon.addonValue} %`}}</span>    
                        </div>
                    </div>
                </div>
                <div :class="[`grid md:grid-cols-${state.meta.quantitiesColumnLength} gap-x-2 divide-x`]">
                    <div v-for="(cost, a) in state.paginate(addon.costs)" :key="a" class="grid">
                        <div class="flex text-xs my-auto">
                            <div class="text-right w-2/5">
                            </div>
                            <div class="ml-1 w-3/5 flex justify-between">
                                <span>=</span>
                                <span>{{formatMoney(cost.addonCost)}}</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>


        <!-- Total for all materials -->
        <div class="grid grid-cols-2 mt-2">
            <div class="text-sm">
                <div v-if="state.data.costAddons.length == 0"
                    class="ml-8 py-1 italic">None</div>
            </div>
            <div :class="`grid grid-cols-${state.meta.quantitiesColumnLength} gap-x-2`">
                <div v-for="(quantity, x) in state.paginate(state.data.quantities)" :key="x">
                    <div class="text-xs flex py-1">
                        <div class="w-2/5 text-right italic"></div>
                        <div class="ml-1 w-3/5 flex justify-between">
                            <span class="mr-1">=</span>
                            <span class="font-bold">
                                {{state.getTotalCostByQuantity(quantity)}}</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>

    </div>
</template>
<script>
import {reactive, inject, computed, watch} from 'vue';
import {formatMoney as formatCurrency} from '@/utils/format.js'

class Cost {
    constructor(orderQuantity, addonCost) {
        this._state = reactive({
            orderQuantity, addonCost
        });
    }

    set orderQuantity(value){this._state.orderQuantity = value}
    get orderQuantity(){return this._state.orderQuantity}

    set addonCost(value){this._state.addonCost = value}
    get addonCost(){return this._state.addonCost}
}

class CostAddon {
    constructor(id, name, sequence, type, addonValue, costs=[]) {
        this._state = reactive({
            id, name, sequence, type, addonValue, costs
        });
    }

    set id(value){this._state.id = value}
    get id(){return this._state.id}

    set name(value){this._state.name = value}
    get name(){return this._state.name}

    set type(value){this._state.type = value}
    get type(){return this._state.type}

    set addonValue(value){this._state.addonValue = value}
    get addonValue(){return this._state.addonValue}

    set costs(value){this._state.costs = value}
    get costs(){return this._state.costs}

    getCostByQuantity(quantity) {
        const cost = this.costs.find(x => x.orderQuantity == quantity);
        return cost? parseFloat(cost.addonCost) : 0;
    }
}

export default {
    props: {
        quantities: {
            type: Array,
            default: ()=>[]
        },
        costAddons: Array,
        quantityViewableOffset: {
            type: Number,
            default: 0
        },
        maxQuantityViewable: {
            type: Number,
            default: 2
        }
    },
    emits: ['initialized'],
    setup(props, {emit}) {
        const currency = inject('currency').abbreviation;
        const state = reactive({
            data: {
                quantities: computed(()=>props.quantities),
                costAddons: []
            },
            meta: {
                quantitiesColumnLength: computed(()=> 
                    Math.min(state.data.quantities.length, 
                        props.maxQuantityViewable)
                ),
                totals: computed(()=> {
                    const costs = state.data.quantities.map(x => {
                        const costAddonPrices = state.data.costAddons
                            .map(y=> y.getCostByQuantity(x));
                        return {
                            quantity: x,
                            cost: costAddonPrices.reduce((a,b)=>a+b, 0)
                        }
                    });
                    return costs;
                })
            },
            paginate: (array) => {
                let spliced = [...array];
                if (array) spliced = spliced.splice(
                    props.quantityViewableOffset, 
                    state.meta.quantitiesColumnLength);
                return spliced;
            },
            getTotalCostByQuantity: (quantity, format=true)=> {
                let total = 0;
                if (quantity > 0){
                    const cost = state.meta.totals.find(x=>x.quantity == quantity);
                    if (cost) total = cost.cost;
                }
                return (format)? formatMoney(total) : total;
            }
        });

        const initializeCostAddons = ()=> {
            state.data.costAddons = [];
            if (props.costAddons && props.costAddons.length > 0) {
                let addons_map = {}

                // Transpose to display format friendly structure
                props.costAddons.forEach(x => {
                    x.addonCosts.forEach(y => {
                        let addon = addons_map[y.id]
                        if (addon == null) {
                            addon = new CostAddon(y.id, y.name, 
                                y.sequence, y.type, y.addonValue);
                            addons_map[y.id] = addon;
                        }
                        const cost = new Cost(x.orderQuantity, y.addonCost);
                        addon.costs.push(cost);
                    });
                });
                Object.entries(addons_map).forEach(([, value]) => {
                    state.data.costAddons.push(value)
                });

                // Initialize totals
                const totals = {};
                state.meta.totals.forEach(x => {
                    totals[x.quantity] = x.cost;
                });
                emit('initialized', totals); 
            }
        }

        const formatMoney = (amount)=> {
            if (amount != null)
                return formatCurrency(amount, currency)
            else return ''
        }

        watch(()=> props.costAddons, initializeCostAddons);

        return {
            state, formatMoney
        }
    },
}
</script>
