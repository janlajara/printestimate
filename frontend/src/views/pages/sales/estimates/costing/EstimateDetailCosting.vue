<template>
    <Section heading="Cost Breakdown">
        <div class="w-full p-4 bg-gray-100 rounded-md">
            <!-- Expand/Collapse Button -->
            <div class="flex justify-end mb-3 cursor-pointer">
                <span class="material-icons bg-gray-300 rounded-full p-1"
                    @click="state.components.expandButton.toggleAll">
                    {{state.components.expandButton.isAllExpanded? 'unfold_less' : 'unfold_more'}}
                </span>
            </div>
            <!-- Table Header -->
            <div class="border-b grid grid-cols-2">
                <div class="hidden sm:grid">
                </div>
                <div class="flex relative col-span-2 sm:col-span-1">
                    <div class="absolute">
                        <span class="material-icons text-xl sm:text-sm cursor-pointer"
                            :class="state.components.paginator.offset == 0? 
                                'hidden': ''"
                            @click="state.components.paginator.left">chevron_left</span>
                    </div>
                    <div :class="`w-full grid grid-cols-${state.meta.quantitiesColumnLength} divide-x`">
                        <div v-for="(quantity, key) in 
                                state.components.paginator.paginate(state.data.quantities)" :key="key"
                            class="flex justify-center">
                            <span class="font-bold text-secondary text-lg sm:text-base">{{quantity}}</span>
                        </div>
                    </div>
                    <div class="absolute right-0">
                        <span class="material-icons text-xl sm:text-sm cursor-pointer"
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
                :max-quantity-viewable="state.meta.maxQuantitiesColumnLength"
                @initialized="value => state.meta.materialTotalsMap = value"
                @toggled="value => state.components.expandButton.materials = value"/>
                
            <!-- Table Rows for Services -->
            <EstimateDetailCostingServices class="py-2"
                :quantities="state.data.quantities"
                :services="state.data.services"
                :quantity-viewable-offset="state.components.paginator.offset"
                :max-quantity-viewable="state.meta.maxQuantitiesColumnLength"
                @initialized="value => state.meta.serviceTotalsMap = value"
                @toggled="value => state.components.expandButton.services = value"/>

            <!-- Table Rows for Cost-addons -->
            <EstimateDetailCostingCostAddons class="py-2 pb-4"
                :quantities="state.data.quantities"
                :cost-addons="state.data.costAddons"
                :quantity-viewable-offset="state.components.paginator.offset"
                :max-quantity-viewable="state.meta.maxQuantitiesColumnLength"
                @initialized="value => state.meta.addonsTotalsMap = value"/>

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
import EstimateDetailCostingCostAddons from './EstimateDetailCostingCostAddons.vue';

import {reactive, inject, computed, onMounted, onUnmounted} from 'vue';
import {formatMoney as formatCurrency} from '@/utils/format.js'
import {getCurrentBreakpoint} from '@/utils/tailwind.js';

export default {
    components: {
        Section, EstimateDetailCostingBillOfMaterials, 
        EstimateDetailCostingServices, EstimateDetailCostingCostAddons
    },
    props: {
        isProcessing: Boolean,
        maxQuantitiesDisplay: {
            type: Number,
            default: 3
        },
        quantities: Array,
        billOfMaterials: Array,
        services: Array,
        costAddons: Array,
    },
    setup(props) {
        const currency = inject('currency').abbreviation;
        const state = reactive({
            meta: {
                isBreakpointBelowLg: false,
                maxQuantitiesColumnLength: computed(()=> 
                    state.meta.isBreakpointBelowLg? 
                        1 : props.maxQuantitiesDisplay
                ),
                quantitiesColumnLength: computed(()=> 
                    Math.min(state.data.quantities.length, 
                        state.meta.maxQuantitiesColumnLength)),
                materialTotalsMap: {},
                serviceTotalsMap: {},
                addonsTotalsMap: {},
                totalsMap: computed(()=> {
                    let totals = {};
                    state.data.quantities.forEach(q=> {
                        const materialTotal = state.meta.materialTotalsMap[q] | 0;
                        const serviceTotal = state.meta.serviceTotalsMap[q] | 0;
                        const addonsTotal = state.meta.addonsTotalsMap[q] | 0;
                        const total = materialTotal + serviceTotal + addonsTotal;
                        totals[q] = total;
                    });
                    return totals;
                })
            },
            data: computed(()=> ({
                quantities: props.quantities,
                billOfMaterials: props.billOfMaterials,
                services: props.services,
                costAddons: props.costAddons
            })),
            components: {
                expandButton: {
                    isAllExpanded: computed(()=> 
                        state.components.expandButton.materials.areAllExpanded &&
                        state.components.expandButton.services.areAllExpanded),
                    materials: {
                        areAllExpanded: false,
                        toggle: ()=>{}
                    },
                    services: {
                        areAllExpanded: false,
                        toggle: ()=>{}
                    },
                    toggleAll: ()=> {
                        const materialsExpanded = state.components.expandButton.materials.areAllExpanded;
                        const servicesExpanded = state.components.expandButton.services.areAllExpanded;
                        if (!materialsExpanded || servicesExpanded)
                            state.components.expandButton.materials.toggle();
                        if (!servicesExpanded || materialsExpanded)
                            state.components.expandButton.services.toggle();
                    }
                },
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

        const onWindowResize = ()=> {
            const breakpoint = getCurrentBreakpoint();
            state.meta.isBreakpointBelowLg = [undefined, 'sm', 'md'].includes(breakpoint);
        } 
        onMounted(()=> {
            onWindowResize();
            window.addEventListener("resize", onWindowResize);
        });
        onUnmounted(()=> {
            window.removeEventListener("resize", onWindowResize);
        });

        return {
            state, formatMoney
        }
    },
    
}
</script>
