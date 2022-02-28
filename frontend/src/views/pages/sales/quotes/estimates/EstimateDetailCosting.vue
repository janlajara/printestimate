<template>
    <Section heading="Cost Estimation">
        <div class="w-full">
            <!-- Table Header -->
            <div class="border-b grid grid-cols-2">
                <div class="font-bold text-lg text-left"></div>
                <div class="flex relative">
                    <div class="absolute">
                        <span class="material-icons text-sm cursor-pointer"
                            :class="state.components.paginator.offset == 0? 
                                'hidden': ''"
                            @click="state.components.paginator.left">chevron_left</span>
                    </div>
                    <div :class="`w-full grid grid-cols-${state.meta.quantitiesColumnLength}`">
                        <div v-for="(quantity, key) in 
                                state.components.paginator.paginate(state.data.quantities)" :key="key"
                            class="flex justify-center">
                            <span class="font-bold">{{quantity}}</span>
                        </div>
                    </div>
                    <div class="absolute right-0">
                        <span class="material-icons text-sm cursor-pointer"
                            :class="state.components.paginator.offset == state.components.paginator.limit? 
                                'hidden': ''"
                            @click="state.components.paginator.right">chevron_right</span>
                    </div>
                </div>
            </div>

            <!-- Table Rows for Bill of Materials -->
            <EstimateDetailCostingBillOfMaterials class="py-2"
                :quantities="state.data.quantities"
                :bill-of-materials="state.data.billOfMaterials"
                :quantity-viewable-offset="state.components.paginator.offset"
                :max-quantity-viewable="3"
                @initialized="value => state.meta.materialTotalsMap = value"/>
                
            <!-- Table Rows for Services -->
            <EstimateDetailCostingServices class="py-2 pb-4"
                :quantities="state.data.quantities"
                :services="state.data.services"
                :quantity-viewable-offset="state.components.paginator.offset"
                :max-quantity-viewable="3"
                @initialized="value => state.meta.serviceTotalsMap = value"/>

                <!-- Table Footer Totals -->
            <div class="border-t pt-2 grid grid-cols-2">
                <div class="text-right">
                    <div class="text-xs py-1">Unit Price:</div>
                    <div class="py-1">Total Price:</div>
                </div>
                <div :class="`w-full grid grid-cols-${state.meta.quantitiesColumnLength}`">
                    <div v-for="(quantity, key) in 
                            state.components.paginator.paginate(state.data.quantities)" :key="key"
                        class="grid">
                        <div class="text-xs flex justify-end my-auto">
                            <div class="ml-1">
                                <span class="text-sm">
                                    {{formatMoney(state.meta.totalsMap[quantity] / quantity)}}
                                </span>
                            </div>
                        </div>
                        <div class="text-xs flex justify-end my-auto">
                            <div class="ml-1">
                                <span class="font-bold text-lg">
                                    {{formatMoney(state.meta.totalsMap[quantity])}}
                                </span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

        </div>
    </Section>
</template>

<script>
import Section from '@/components/Section.vue';
import EstimateDetailCostingBillOfMaterials from './EstimateDetailCostingBillOfMaterials.vue';
import EstimateDetailCostingServices from './EstimateDetailCostingServices.vue';

import {reactive, inject, computed} from 'vue';
import {formatMoney as formatCurrency} from '@/utils/format.js'

export default {
    components: {
        Section, EstimateDetailCostingBillOfMaterials, EstimateDetailCostingServices
    },
    props: {
        isProcessing: Boolean,
        maxQuantitiesDisplay: {
            type: Number,
            default: 3
        },
        quantities: Array,
        billOfMaterials: Array,
        services: Array
    },
    setup(props) {
        const currency = inject('currency').abbreviation;
        const state = reactive({
            meta: {
                maxQuantitiesColumnLength: props.maxQuantitiesDisplay,
                quantitiesColumnLength: computed(()=> 
                    Math.min(state.data.quantities.length, 
                        state.meta.maxQuantitiesColumnLength)),
                materialTotalsMap: {},
                serviceTotalsMap: {},
                totalsMap: computed(()=> {
                    let totals = {};
                    state.data.quantities.forEach(q=> {
                        const materialTotal = state.meta.materialTotalsMap[q] | 0;
                        const serviceTotal = state.meta.serviceTotalsMap[q] | 0;
                        const total = materialTotal + serviceTotal;
                        totals[q] = total;
                    });
                    return totals;
                })
            },
            data: computed(()=> ({
                quantities: props.quantities,
                billOfMaterials: props.billOfMaterials,
                services: props.services
            })),
            components: {
                paginator: {
                    offset: 0,
                    limit: computed(()=>
                        state.data.quantities.length - state.meta.quantitiesColumnLength),
                    paginate: (array)=> {
                        let spliced = [...array];
                        if (array) spliced = spliced.splice(
                            state.components.paginator.offset, 
                            state.meta.quantitiesColumnLength);
                        return spliced;
                    },
                    left: ()=> {
                        let offset = state.components.paginator.offset - 1;
                        state.components.paginator.offset = Math.max(offset, 0);
                    },
                    right: ()=> {
                        let offset = state.components.paginator.offset + 1;
                        let limit = state.components.paginator.limit;
                        state.components.paginator.offset = Math.min(offset, limit);
                    }
                }
            }
        });

        const formatMoney = (amount)=> {
            if (amount != null)
                return formatCurrency(amount, currency)
            else return ''
        }
        return {
            state, formatMoney
        }
    },
    
}
</script>
