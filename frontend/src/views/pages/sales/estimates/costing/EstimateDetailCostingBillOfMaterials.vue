<template>
    <div>
        <!-- Table Rows for Bill of Materials -->
        <div class="flex text-primary-dark font-bold">
            <span>Bill of Materials</span>
        </div>
        <div v-for="(material, x) in state.data.billOfMaterials" :key="x"
            :class="!material.isExpanded? 'border-b' : ''">
            <div class="grid" :class="!material.isExpanded? 'grid-cols-2' : ''">
                <div class="cursor-pointer" 
                    @click="()=>{
                        material.isExpanded = !material.isExpanded;
                        emitToggled()}">
                    <div class="flex">
                        <span class="material-icons text-base my-auto transition"
                            :class="material.isExpanded? 'transform rotate-90': ''">
                            chevron_right</span>
                        <div class="ml-4">
                            <span class="text-sm">
                                {{material.name}}</span>
                        </div> 
                        <div class="ml-4 flex-auto text-right hidden lg:block" 
                            v-show="!material.isExpanded">
                            <span class="text-xs">
                                {{formatMoney(material.rate)}} / {{material.uom}}</span>    
                        </div>
                    </div>
                </div>
                <div :class="[`grid md:grid-cols-${state.meta.quantitiesColumnLength} gap-x-2 divide-x transition`,
                    material.isExpanded? 'transform opacity-0 ': '']">
                    <div v-for="(estimate, y) in state.paginate(material.estimates)" :key="y" class="grid">
                        <div class="text-xs flex my-auto">
                            <div class="text-right w-2/5">
                                <span class="text-gray-500">x</span>
                                {{roundNumber(estimate.totalQuantity, 4)}}</div>
                            <div class="ml-1 w-3/5 flex justify-between">
                                <span class="text-gray-500">=</span>
                                <span>{{formatMoney(material.rate * estimate.totalQuantity)}}</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            <transition 
                enter-active-class="transition ease-out duration-100" 
                enter-from-class="transform origin-top opacity-0 scale-y-75" 
                enter-to-class="transform origin-top opacity-100 scale-100" 
                leave-active-class="transition ease-in duration-75" 
                leave-from-class="transform origin-top opacity-100 scale-100" 
                leave-to-class="transform origin-top opacity-0 scale-y-75">
                <div v-show="material.isExpanded" class="border-b pb-2">
                    <EstimateDetailCostingBillOfMaterialsLayout
                        :machine-type="material.machineType"
                        :layouts="material.layouts"/>
                    <div class="border-t-2 border-dotted text-gray-500 grid grid-cols-2">
                        <div>
                            <div class="flex">
                                <div class="ml-8 text-sm my-auto">Stock Quantity</div>
                                <div class="ml-4 flex-auto text-right">
                                    <span class="text-xs">
                                        {{formatMoney(material.rate)}} / {{material.uom}}</span>    
                                </div>
                            </div>                              
                        </div>
                        <div :class="`grid grid-cols-${state.meta.quantitiesColumnLength} gap-x-2 divide-x`">
                            <div v-for="(estimate, y) in state.paginate(material.estimates)" :key="y" class="grid">
                                <div class="text-xs flex my-auto">
                                    <div class="text-right w-2/5">
                                        <span>x</span>
                                        {{estimate.estimatedQuantity}}</div>
                                    <div class="ml-1 w-3/5 flex justify-between">
                                        <span>=</span>
                                        <span>{{formatMoney(material.rate * estimate.estimatedQuantity)}}</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="border-t-2 border-dotted text-gray-500 grid grid-cols-2">
                        <div>
                            <div class="flex">
                                <div class="ml-8 text-sm my-auto">Spoilage ({{material.spoilageRate}}%)</div>
                                <div class="ml-4 flex-auto text-right">
                                    <span class="text-xs">
                                        {{formatMoney(material.rate)}} / {{material.uom}}</span>    
                                </div>
                            </div>
                        </div>
                        <div :class="`grid grid-cols-${state.meta.quantitiesColumnLength} gap-x-2 divide-x`">
                            <div v-for="(estimate, y) in state.paginate(material.estimates)" :key="y" class="grid">
                                <div class="text-xs flex my-auto">
                                    <div class="text-right w-2/5">
                                        <span>x</span>
                                        {{estimate.spoilageQuantity}}</div>
                                    <div class="ml-1 w-3/5 flex justify-between">
                                        <span>=</span>
                                        <span>{{formatMoney(material.rate * estimate.spoilageQuantity)}}</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    <!-- Total for a material -->
                    <div class="border-t-2 border-dotted grid grid-cols-2 mb-4">
                        <div>
                        </div>
                        <div :class="`grid grid-cols-${state.meta.quantitiesColumnLength} gap-x-2 divide-x`">
                            <div v-for="(estimate, y) in state.paginate(material.estimates)" :key="y" class="grid">
                                <div class="text-xs flex py-1 my-auto">
                                    <div class="text-right w-2/5">
                                        <span>x</span>
                                        {{roundNumber(estimate.totalQuantity, 4)}}</div>
                                    <div class="ml-1 w-3/5 flex justify-between">
                                        <span>=</span>
                                        <span class="underline">
                                            {{formatMoney(material.rate * estimate.totalQuantity)}}</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </transition>
        </div>
        <!-- Total for all materials -->
        <div class="grid grid-cols-2 mt-2">
            <div class="text-right text-xs">
                <div class="py-1"></div>
            </div>
            <div :class="`grid grid-cols-${state.meta.quantitiesColumnLength} gap-x-2`">
                <div v-for="(quantity, x) in state.paginate(state.data.quantities)" :key="x">
                    <div class="text-xs flex py-1">
                        <div class="w-2/5 text-right italic"></div>
                        <div class="ml-1 w-3/5 flex justify-between">
                            <span class="mr-1">=</span>
                            <span class="font-bold">
                                {{state.getMaterialTotalPriceByQuantity(quantity)}}</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import EstimateDetailCostingBillOfMaterialsLayout from './EstimateDetailCostingBillOfMaterialsLayout.vue';

import {reactive, inject, computed, watch} from 'vue';
import {roundNumber, formatMoney as formatCurrency} from '@/utils/format.js'

class Material {
    constructor(name, rate, uom, spoilageRate, estimates, 
            currency, layouts, machineType) {
        this._state = reactive({
            name, rate, uom, spoilageRate, estimates, 
            currency, layouts, machineType,
            isExpanded: false
        })
    }

    set isExpanded(value){this._state.isExpanded = value}
    get isExpanded(){return this._state.isExpanded}

    set name(value){this._state.name = value}
    get name(){return this._state.name}

    set rate(value){this._state.rate = value}
    get rate(){return this._state.rate}

    set uom(value){this._state.uom = value}
    get uom(){return this._state.uom}

    set spoilageRate(value){this._state.spoilageRate = value}
    get spoilageRate(){return this._state.spoilageRate}

    set estimates(value){this._state.estimates = value}
    get estimates(){return this._state.estimates}

    set currency(value){this._state.currency = value}
    get currency(){return this._state.currency}

    set layouts(value){this._state.layouts = value}
    get layouts(){return this._state.layouts}

    set machineType(value){this._state.machineType = value}
    get machineType(){return this._state.machineType}

    get rateLabel() {
        return formatCurrency(this._state.rate, this._state.currency)
    }

    getTotalPriceByQuantity(quantity) {
        const estimate = this.estimates.find(x=>x.itemQuantity == quantity);
        return estimate.totalQuantity * this.rate;
    }
}

class MaterialEstimate {
    constructor(itemQuantity, estimatedQuantity, spoilageQuantity){
        this._state = reactive({
            itemQuantity, estimatedQuantity, spoilageQuantity
        })
    }

    get totalQuantity(){return computed(()=> 
        this.estimatedQuantity + this.spoilageQuantity);}

    set itemQuantity(value){this._state.itemQuantity = value}
    get itemQuantity(){return this._state.itemQuantity}

    set estimatedQuantity(value){this._state.estimatedQuantity = value}
    get estimatedQuantity(){return parseFloat(this._state.estimatedQuantity)}

    set spoilageQuantity(value){this._state.spoilageQuantity = value}
    get spoilageQuantity(){return parseFloat(this._state.spoilageQuantity)}
}

export default {
    components: {
        EstimateDetailCostingBillOfMaterialsLayout
    },
    props: {
        quantities: {
            type: Array,
            default: ()=>[]
        },
        billOfMaterials: Array,
        quantityViewableOffset: {
            type: Number,
            default: 0
        },
        maxQuantityViewable: {
            type: Number,
            default: 2
        }
    },
    emits: ['initialized', 'toggled'],
    setup(props, {emit}) {
        const currency = inject('currency').abbreviation;
        const state = reactive({
            meta: {
                areAllMaterialsExpanded: computed(()=>
                    state.data.billOfMaterials.filter(material => 
                        !material.isExpanded).length == 0
                ),
                quantitiesColumnLength: computed(()=> 
                    Math.min(state.data.quantities.length, 
                        props.maxQuantityViewable)
                ),
                totals: {
                    materials: computed(()=> {
                        let estimates = state.data.quantities.map(x=> {
                            const materialPrices = state.data.billOfMaterials.map(y=>
                                y.getTotalPriceByQuantity(x));
                            return {
                                quantity: x,
                                price: materialPrices.reduce((a,b)=>a+b, 0)
                            }
                        });
                        return estimates;
                    })
                },
                displayedQuantities: computed(()=>
                    state.paginate(state.data.quantities))
            },
            data: {
                quantities: computed(()=>props.quantities),
                billOfMaterials: []
            },
            getMaterialTotalPriceByQuantity: (quantity=0, format=true) => {
                let price = 0;
                if (quantity > 0){
                    const material = state.meta.totals.materials.find(x=>x.quantity == quantity);
                    if (material) price = material.price;
                }
                return (format)? formatMoney(price) : price;
            },
            paginate: (array) => {
                let spliced = [...array];
                if (array) spliced = spliced.splice(
                    props.quantityViewableOffset, 
                    state.meta.quantitiesColumnLength);
                return spliced;
            }
        });

        const emitToggled = ()=> {
            const areAllExpanded = state.meta.areAllMaterialsExpanded;
            const toggle = ()=> {
                state.data.billOfMaterials
                    .filter(material => material.isExpanded == state.meta.areAllMaterialsExpanded)
                    .forEach(material => {
                        material.isExpanded = !material.isExpanded;
                });
                emitToggled();
            }
            emit('toggled', {
                areAllExpanded, toggle
            });
        }

        const initializeBillOfMaterials = ()=> {
            state.data.billOfMaterials = [];
            if (props.billOfMaterials) {
                props.billOfMaterials.forEach(data => {
                    const estimates = data.estimates.map(x=> 
                        new MaterialEstimate(
                            x.itemQuantity, x.estimatedMaterialQuantity,
                            x.spoilageMaterialQuantity));
                    const material = new Material(data.name, data.rate, 
                        data.uom, data.spoilageRate, estimates, currency, 
                        data.layouts, data.machineType);
                    state.data.billOfMaterials.push(material); 
                });

                let totals = {};
                state.data.quantities.forEach(q => 
                    totals[q] = state.getMaterialTotalPriceByQuantity(q, false))
                emit('initialized', totals); 
                emitToggled();
            }
        }

        const formatMoney = (amount)=> {
            if (amount != null)
                return formatCurrency(amount, currency)
            else return ''
        }

        watch(()=>props.billOfMaterials, initializeBillOfMaterials);

        return {
            state, formatMoney, roundNumber, emitToggled
        }
    }
}
</script>