<template>
    <Page :title="`Estimate : ${state.data.estimateCode}`">
        <hr class="my-4"/>
        <div class="flex gap-4">
            <Button color="secondary" icon="arrow_back"
                @click="()=>$router.go(-1)">Go Back</Button>
            <Button class="my-auto" icon="edit"
                @click="state.components.editModal.open"/>
            <Button icon="delete" 
                @click="state.components.deleteDialog.open"/>
            <DeleteRecordDialog 
                heading="Delete Quote"
                :is-open="state.components.deleteDialog.isOpen"
                :execute="state.components.deleteDialog.delete"
                :on-after-execute="()=>$router.go(-1)"
                @toggle="state.components.deleteDialog.toggle">
                <div>
                    Are you sure you want to delete 
                    <span class="font-bold">
                        {{state.data.estimateCode}}</span>?
                </div>
            </DeleteRecordDialog>
        </div>
        <Section>
            <DescriptionList class="md:grid-cols-3">
                <DescriptionItem  
                    name="Template" :loader="state.isProcessing" 
                    :value="`[${state.data.templateCode}] ${state.data.templateName}`"/>
                <DescriptionItem :loader="state.isProcecssing"
                    name="Description" :value="state.data.templateDescription"/>
            </DescriptionList>
        </Section>
        <Section>
            <div class="w-full">
                <!-- Table Header -->
                <div class="border-b grid grid-cols-2">
                    <div class="font-bold text-lg text-left">
                        Cost Estimation</div>
                    <div :class="`grid grid-cols-${state.meta.quantitiesColumnLength}`">
                        <div v-for="(quantity, key) in state.data.quantities" :key="key"
                            class="flex justify-center">
                            <span class="font-bold">{{quantity}}</span>
                        </div>
                    </div>
                </div>

                <!-- Table Rows for Bill of Materials -->
                <div class="pt-4 text-primary-dark font-bold">
                    <span>Bill of Materials</span>
                </div>
                <div v-for="(material, x) in state.data.billOfMaterials" :key="x"
                    class="border-b">
                    <div class="grid md:grid-cols-2">
                        <div class="cursor-pointer" 
                            @click="()=>{material.isExpanded = !material.isExpanded}">
                            <div class="flex my-auto">
                                <span class="material-icons text-base my-auto">
                                    {{material.isExpanded? 
                                        'expand_more' : 'chevron_right'}}</span>
                                <div class="ml-4">
                                    <span class="text-sm">
                                        {{material.name}}</span>
                                </div> 
                                <div class="ml-4 flex-auto text-right">
                                    <span class="text-xs">
                                        {{formatMoney(material.rate)}} / {{material.uom}}</span>    
                                </div>
                            </div>
                        </div>
                        <div :class="`grid md:grid-cols-${state.meta.quantitiesColumnLength}`">
                            <div v-for="(estimate, y) in material.estimates" :key="y" class="my-auto">
                                <div class="text-xs flex">
                                    <div class="text-right md:w-2/5">
                                        <span class="text-gray-500">x</span>
                                        {{estimate.totalMaterialQuantity}}</div>
                                    <div class="text-left ml-1 md:w-3/5">
                                        <span class="text-gray-500">=</span>
                                        {{formatMoney(material.rate * estimate.totalMaterialQuantity)}}</div>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div v-show="material.isExpanded"
                        class="border-t-2 border-dotted text-gray-500 grid grid-cols-2">
                        <div>
                            <div class="flex">
                                <div class="ml-8 text-sm my-auto">Stock Quantity</div>
                                <div class="ml-4 flex-auto text-right">
                                    <span class="text-xs">
                                        {{formatMoney(material.rate)}} / {{material.uom}}</span>    
                                </div>
                            </div>                              
                        </div>
                        <div :class="`grid grid-cols-${state.meta.quantitiesColumnLength}`">
                            <div v-for="(estimate, y) in material.estimates" :key="y" class="my-auto">
                                <div class="text-xs flex">
                                    <div class="text-right w-2/5">
                                        <span>x</span>
                                        {{estimate.estimatedMaterialQuantity}}</div>
                                    <div class="text-left ml-1">
                                        <span>=</span>
                                        {{formatMoney(material.rate * estimate.estimatedMaterialQuantity)}}</div>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div v-show="material.isExpanded"
                        class="border-t-2 border-dotted text-gray-500 grid grid-cols-2">
                        <div>
                            <div class="flex">
                                <div class="ml-8 text-sm my-auto">Spoilage ({{material.spoilageRate}}%)</div>
                                <div class="ml-4 flex-auto text-right">
                                    <span class="text-xs">
                                        {{formatMoney(material.rate)}} / {{material.uom}}</span>    
                                </div>
                            </div>
                        </div>
                        <div :class="`grid grid-cols-${state.meta.quantitiesColumnLength}`">
                            <div v-for="(estimate, y) in material.estimates" :key="y" class="my-auto">
                                <div class="text-xs flex">
                                    <div class="text-right w-2/5">
                                        <span>x</span>
                                        {{estimate.spoilageMaterialQuantity}}</div>
                                    <div class="text-left ml-1">
                                        <span>=</span>
                                        {{formatMoney(material.rate * estimate.spoilageMaterialQuantity)}}</div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                <!-- Total for Bill of Materials -->
                <div class="grid grid-cols-2 mt-1">
                    <div>
                    </div>
                    <div :class="`grid grid-cols-${state.meta.quantitiesColumnLength}`">
                        <div v-for="(quantity, x) in state.data.quantities" :key="x">
                            <div class="text-xs flex">
                                <div class="w-2/5"></div>
                                <div class="ml-1">
                                    <span class="mr-1">=</span>
                                    <span class="underline">
                                        {{state.getMaterialTotalPriceByQuantity(quantity)}}</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Table Rows for Bill of Materials -->
                <div class="pt-4 text-primary-dark font-bold">
                    <span>Services</span>
                </div>
                <div v-for="(service, w) in state.data.services" :key="w"
                    class="border-b">
                    <div class="grid grid-cols-2">
                        <div class="cursor-pointer" 
                            @click="()=>{service.isExpanded = !service.isExpanded}">
                            <div class="flex  my-auto">
                                <span class="material-icons text-base my-auto">
                                    {{service.isExpanded? 
                                        'expand_more' : 'chevron_right'}}</span>
                                <div class="ml-4">
                                    <span class="text-sm inline-block align-middle">
                                        {{service.name}}</span>
                                </div>
                            </div>
                        </div>
                        <div :class="`grid grid-cols-${state.meta.quantitiesColumnLength}`">
                            <div v-for="(quantity, a) in state.data.quantities" :key="a" class="my-auto">
                                <div class="flex text-xs">
                                    <div class="text-right w-2/5">
                                    </div>
                                    <div class="text-left ml-1">
                                        <span>=</span>
                                        {{formatMoney(quantity)}}
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <div v-for="(operation, x) in service.operations" :key="x" v-show="service.isExpanded" 
                        class="border-t-2 border-dotted text-gray-500 text-sm">
                        <span class="ml-8">{{operation.name}}</span>
                        <div v-for="(activity, y) in operation.activities" :key="y"
                            class="border-t-2 border-dotted">
                            <span class="ml-12">{{activity.name}}</span>
                            <div v-for="(expense, z) in activity.expenses" :key="z"
                                class="border-t-2 border-dotted  grid grid-cols-2">
                                <div class="flex">
                                    <div class="ml-16">{{expense.name}}</div>
                                    <div class="ml-4 flex-auto text-right">
                                        <span class="text-xs inline-block align-middle">
                                            {{formatMoney(expense.rate)}} 
                                            {{({hour: '/ hr', 
                                                measure: `/ ${service.uom}`, 
                                                flat: ''})[expense.type]}}</span>    
                                    </div>
                                </div>
                                <div :class="`grid grid-cols-${state.meta.quantitiesColumnLength}`">
                                    <div v-for="(estimate, a) in expense.estimates" :key="a" class="my-auto">
                                        <div class="flex text-xs">
                                            <div class="text-right w-2/5"
                                                :class="estimate.estimate == null? 'invisible' : ''">
                                                <span>x</span>
                                                {{estimate.estimate}}</div>
                                            <div class="text-left ml-1">
                                                <span>=</span>
                                                {{formatMoney(expense.rate * (estimate.estimate || 1))}}</div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </Section>
    </Page>
    
</template>
<script>
import Page from '@/components/Page.vue';
import Button from '@/components/Button.vue';
import Section from '@/components/Section.vue';
import DeleteRecordDialog from '@/components/DeleteRecordDialog.vue';
import DescriptionList from '@/components/DescriptionList.vue';
import DescriptionItem from '@/components/DescriptionItem.vue';

import {reactive, inject, computed} from 'vue';
import {formatQuantity, formatMoney as formatCurrency} from '@/utils/format.js'

export default {
    components: {
        Page, Button, Section, DeleteRecordDialog, DescriptionList, DescriptionItem
    },
    setup() {
        const currency = inject('currency').abbreviation
        const state = reactive({
            isProcessing: false,
            meta: {
                quantitiesColumnLength: computed(()=> Math.max(state.data.quantities.length, 1))
            },
            data: {
                estimateCode: 'CE-1234',
                templateCode: 'PT-9876',
                templateName: 'Carbonless Form',
                templateDescription: '8.5x11" Carbonless Form (White, Yellow, Blue)',
                quantities: [100, 200, 300],
                billOfMaterials: [
                    {name: 'Generic Carbonless White 32x24inch', 
                     rate: 30.00, rateLabel: '₱30.00',
                     uom: 'sheet', 
                     spoilageRate: 0, isExpanded: false,
                     estimates: [
                        {itemQuantity: 100, 
                          estimatedMaterialQuantity: 300,
                          spoilageMaterialQuantity: 0,
                          totalMaterialQuantity: 300},
                        {itemQuantity: 200, 
                          estimatedMaterialQuantity: 600,
                          spoilageMaterialQuantity: 0,
                          totalMaterialQuantity: 600},
                        {itemQuantity: 300, 
                          estimatedMaterialQuantity: 900,
                          spoilageMaterialQuantity: 0,
                          totalMaterialQuantity: 900}
                     ]},
                     {name: 'Carbonless Blue 32x24', 
                     rate: 30.00, rateLabel: '₱30.00',
                     uom: 'sheet', 
                     spoilageRate: 0, isExpanded: false,
                     estimates: [
                        {itemQuantity: 100, 
                          estimatedMaterialQuantity: 300,
                          spoilageMaterialQuantity: 0,
                          totalMaterialQuantity: 300},
                        {itemQuantity: 200, 
                          estimatedMaterialQuantity: 600,
                          spoilageMaterialQuantity: 0,
                          totalMaterialQuantity: 600},
                        {itemQuantity: 300, 
                          estimatedMaterialQuantity: 900,
                          spoilageMaterialQuantity: 0,
                          totalMaterialQuantity: 900}
                     ]}
                ],
                services: [
                    {name: 'Raw-to-running cut',
                    uom: 'count', 
                    isExpanded: false,
                    operations: [
                        {name: 'Cutting',
                        activities: [
                            {name: 'Polar Cutter Cutting',
                            expenses: [
                                {name: 'Cut fee', type: 'measure', rate: 50, 
                                estimates: [
                                    {itemQuantity: 100, estimate: 4},
                                    {itemQuantity: 200, estimate: 4},
                                    {itemQuantity: 300, estimate: 4},
                                ]},
                                {name: 'Electricity', type: 'hour', rate: 67, 
                                estimates: [
                                    {itemQuantity: 100, estimate: 8},
                                    {itemQuantity: 200, estimate: 16},
                                    {itemQuantity: 300, estimate: 24},
                                ]},
                                {name: 'Depreciation', type: 'hour', rate: 120, 
                                estimates: [
                                    {itemQuantity: 100, estimate: 8},
                                    {itemQuantity: 200, estimate: 16},
                                    {itemQuantity: 300, estimate: 24},
                                ]},
                                {name: 'Usage fee', type: 'flat', rate: 400, 
                                estimates: [
                                    {itemQuantity: 100, estimate: null},
                                    {itemQuantity: 200, estimate: null},
                                    {itemQuantity: 300, estimate: null},
                                ]},
                            ]}
                        ]}
                    ]},
                    {name: 'Printing',
                    uom: 'sheet', 
                    isExpanded: false,
                    operations: [
                        {name: 'Front Print',
                        activities: [
                            {name: 'Spot Color Printing : 1st Color',
                            expenses: [
                                {name: 'Ink', type: 'measure', rate: 0.50, 
                                estimates: [
                                    {itemQuantity: 100, estimate: 500},
                                    {itemQuantity: 200, estimate: 750},
                                    {itemQuantity: 300, estimate: 1000},
                                ]},
                                {name: 'Electricity', type: 'hour', rate: 66.67, 
                                estimates: [
                                    {itemQuantity: 100, estimate: 16},
                                    {itemQuantity: 200, estimate: 18},
                                    {itemQuantity: 300, estimate: 20},
                                ]},
                                {name: 'Labor', type: 'hour', rate: 75, 
                                estimates: [
                                    {itemQuantity: 100, estimate: 16},
                                    {itemQuantity: 200, estimate: 18},
                                    {itemQuantity: 300, estimate: 20},
                                ]},
                            ]},
                            {name: 'Spot Color Printing : 2nd Color',
                            expenses: [
                                {name: 'Ink', type: 'measure', rate: 0.50, 
                                estimates: [
                                    {itemQuantity: 100, estimate: 500},
                                    {itemQuantity: 200, estimate: 750},
                                    {itemQuantity: 300, estimate: 1000},
                                ]},
                                {name: 'Electricity', type: 'hour', rate: 66.67, 
                                estimates: [
                                    {itemQuantity: 100, estimate: 16},
                                    {itemQuantity: 200, estimate: 18},
                                    {itemQuantity: 300, estimate: 20},
                                ]},
                                {name: 'Labor', type: 'hour', rate: 75, 
                                estimates: [
                                    {itemQuantity: 100, estimate: 16},
                                    {itemQuantity: 200, estimate: 18},
                                    {itemQuantity: 300, estimate: 20},
                                ]},
                            ]},
                        ]},
                        {name: 'Back Print',
                        activities: [
                            {name: 'Spot Color Printing : 1st Color',
                            expenses: [
                                {name: 'Ink', type: 'measure', rate: 0.50, 
                                estimates: [
                                    {itemQuantity: 100, estimate: 500},
                                    {itemQuantity: 200, estimate: 750},
                                    {itemQuantity: 300, estimate: 1000},
                                ]},
                                {name: 'Electricity', type: 'hour', rate: 66.67, 
                                estimates: [
                                    {itemQuantity: 100, estimate: 16},
                                    {itemQuantity: 200, estimate: 18},
                                    {itemQuantity: 300, estimate: 20},
                                ]},
                                {name: 'Labor', type: 'hour', rate: 75, 
                                estimates: [
                                    {itemQuantity: 100, estimate: 16},
                                    {itemQuantity: 200, estimate: 18},
                                    {itemQuantity: 300, estimate: 20},
                                ]},
                            ]},
                            {name: 'Spot Color Printing : 2nd Color',
                            expenses: [
                                {name: 'Ink', type: 'measure', rate: 0.50, 
                                estimates: [
                                    {itemQuantity: 100, estimate: 500},
                                    {itemQuantity: 200, estimate: 750},
                                    {itemQuantity: 300, estimate: 1000},
                                ]},
                                {name: 'Electricity', type: 'hour', rate: 66.67, 
                                estimates: [
                                    {itemQuantity: 100, estimate: 16},
                                    {itemQuantity: 200, estimate: 18},
                                    {itemQuantity: 300, estimate: 20},
                                ]},
                                {name: 'Labor', type: 'hour', rate: 75, 
                                estimates: [
                                    {itemQuantity: 100, estimate: 16},
                                    {itemQuantity: 200, estimate: 18},
                                    {itemQuantity: 300, estimate: 20},
                                ]},
                            ]},
                        ]}
                    ]}
                ]
            },
            components: {
                editModal: {
                    open: ()=> {}
                },
                deleteDialog: {
                    isOpen: false,
                    toggle: value => state.components.deleteDialog.isOpen = value,
                    open: ()=> state.components.deleteDialog.toggle(true),
                    delete: ()=> {}
                }
            },
            getMaterialTotalPriceByQuantity: (quantity=0) => {
                const prices = state.data.billOfMaterials
                    .filter(x=>x.estimates.find(y=>y.itemQuantity == quantity) != null)
                    .map(x=>x.estimates.find(y=>y.itemQuantity == quantity).totalMaterialQuantity * x.rate);
                const totalPrice = prices.reduce((a,b)=> a+b, 0);
                return formatMoney(totalPrice);
            },
            getServicePriceByQuantity: (serviceIndex, quantity=0) => {
                if (serviceIndex && quantity > 0) {
                    const service = state.data.services[serviceIndex];
                    const prices = service.operations.map(x=>
                        x.activities.map(y=> 
                            y.expenses.map(z=> {
                                const estimate = z.estimates.find(a=> a.itemQuantity == quantity) || 0;
                                return estimate.estimate * z.rate;
                            })
                        )
                    )
                    return prices.reduce((a,b)=> a+b, 0);
                }
            } 
        });

        const formatMoney = (amount)=> {
            if (amount != null)
                return formatCurrency(amount, currency)
            else return ''
        }

        return {
            state,
            formatQuantity,
            formatMoney
        }
    }
    
}
</script>