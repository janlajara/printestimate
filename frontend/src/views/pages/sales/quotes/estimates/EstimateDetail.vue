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
                    :class="!material.isExpanded? 'border-b' : ''">
                    <div class="grid md:grid-cols-2">
                        <div class="cursor-pointer" 
                            @click="()=>{material.isExpanded = !material.isExpanded}">
                            <div class="flex">
                                <span class="material-icons text-base my-auto">
                                    {{material.isExpanded? 
                                        'expand_more' : 'chevron_right'}}</span>
                                <div class="ml-4">
                                    <span class="text-sm">
                                        {{material.name}}</span>
                                </div> 
                                <div class="ml-4 flex-auto text-right" 
                                    v-show="!material.isExpanded">
                                    <span class="text-xs">
                                        {{formatMoney(material.rate)}} / {{material.uom}}</span>    
                                </div>
                            </div>
                        </div>
                        <div :class="`grid md:grid-cols-${state.meta.quantitiesColumnLength}`"
                            v-show="!material.isExpanded">
                            <div v-for="(estimate, y) in material.estimates" :key="y" class="my-auto">
                                <div class="text-xs flex">
                                    <div class="text-right w-2/5">
                                        <span class="text-gray-500">x</span>
                                        {{estimate.totalQuantity}}</div>
                                    <div class="ml-1 w-3/5 flex justify-between">
                                        <span class="text-gray-500">=</span>
                                        <span>{{formatMoney(material.rate * estimate.totalQuantity)}}</span>
                                    </div>
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
                                        {{estimate.estimatedQuantity}}</div>
                                    <div class="ml-1 w-3/5 flex justify-between">
                                        <span>=</span>
                                        <span>{{formatMoney(material.rate * estimate.estimatedQuantity)}}</span>
                                    </div>
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
                    <div v-show="material.isExpanded"
                        class="border-t-2 border-dotted grid grid-cols-2 mb-4">
                        <div>
                        </div>
                        <div :class="`grid grid-cols-${state.meta.quantitiesColumnLength}`">
                            <div v-for="(estimate, y) in material.estimates" :key="y" class="my-auto">
                                <div class="text-xs flex py-1">
                                    <div class="text-right w-2/5">
                                        <span>x</span>
                                        {{estimate.totalQuantity}}</div>
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
                <!-- Total for all materials -->
                <div class="grid grid-cols-2 mt-1">
                    <div>
                    </div>
                    <div :class="`grid grid-cols-${state.meta.quantitiesColumnLength}`">
                        <div v-for="(quantity, x) in state.data.quantities" :key="x">
                            <div class="text-xs flex">
                                <div class="w-2/5 text-right italic">Total</div>
                                <div class="ml-1 w-3/5 flex justify-between">
                                    <span class="mr-1">=</span>
                                    <span class="underline">
                                        {{state.getMaterialTotalPriceByQuantity(quantity)}}</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Table Rows for Services -->
                <div class="pt-4 text-primary-dark font-bold">
                    <span>Services</span>
                </div>
                <div v-for="(service, w) in state.data.services" :key="w"
                    :class="!service.isExpanded? 'border-b' : ''">
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
                        <div :class="`grid grid-cols-${state.meta.quantitiesColumnLength}`"
                            v-show="!service.isExpanded">
                            <div v-for="(quantity, a) in state.data.quantities" :key="a" class="my-auto">
                                <div class="flex text-xs">
                                    <div class="text-right w-2/5">
                                    </div>
                                    <div class="ml-1 w-3/5 flex justify-between">
                                        <span>=</span>
                                        <span>{{formatMoney(service.getTotalExpensesByQuantity(quantity))}}</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    <!-- Service Breakdown Expandable -->
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
                                            <div class="ml-1 w-3/5 flex justify-between">
                                                <span>=</span>
                                                <span>{{formatMoney(expense.getEstimatePriceByQuantity(estimate.itemQuantity))}}</span>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    <!-- Service Total Expandable -->
                    <div v-show="service.isExpanded"
                        class="border-t-2 border-dotted grid grid-cols-2 mb-4">
                        <div>
                        </div>
                        <div :class="`grid grid-cols-${state.meta.quantitiesColumnLength}`">
                            <div v-for="(quantity, y) in state.data.quantities" :key="y" class="my-auto">
                                <div class="text-xs flex py-1">
                                    <div class="w-2/5"></div>
                                    <div class="ml-1 w-3/5 flex justify-between">
                                        <span>=</span>
                                        <span class="underline">
                                            {{formatMoney(service.getTotalExpensesByQuantity(quantity))}}</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- Total for all Services -->
                <div class="grid grid-cols-2 mt-1">
                    <div>
                    </div>
                    <div :class="`grid grid-cols-${state.meta.quantitiesColumnLength}`">
                        <div v-for="(quantity, x) in state.data.quantities" :key="x">
                            <div class="text-xs flex">
                                <div class="w-2/5 text-right italic">Total</div>
                                <div class="ml-1 w-3/5 flex justify-between">
                                    <span class="mr-1">=</span>
                                    <span class="underline">
                                        {{state.getServicePriceByQuantity(quantity)}}</span>
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

import {reactive, inject, computed, onBeforeMount} from 'vue';
import {formatQuantity, formatMoney as formatCurrency} from '@/utils/format.js'

class Material {
    constructor(name, rate, uom, spoilageRate, estimates, currency) {
        this._state = reactive({
            name, rate, uom, spoilageRate, estimates, currency,
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
    get estimatedQuantity(){return this._state.estimatedQuantity}

    set spoilageQuantity(value){this._state.spoilageQuantity = value}
    get spoilageQuantity(){return this._state.spoilageQuantity}
}

class Service {
    constructor(name, uom, operations) {
        this._state = reactive({
            name, uom, operations, isExpanded: false
        })
    }

    set name(value){this._state.name = value}
    get name(){return this._state.name}

    set uom(value){this._state.uom = value}
    get uom(){return this._state.uom}

    set operations(value){this._state.operations = value}
    get operations(){return this._state.operations}

    set isExpanded(value){this._state.isExpanded = value}
    get isExpanded(){return this._state.isExpanded}

    getTotalExpensesByQuantity(quantity) {
        const operationPrices = this.operations.map(x=>
            x.getTotalExpensesByQuantity(quantity))
        return operationPrices.reduce((a,b)=> a+b, 0)
    }
}

class Operation {
    constructor(name, activities) {
        this._state = reactive({
            name, activities
        })
    }

    set name(value){this._state.name = value}
    get name(){return this._state.name}

    set activities(value){this._state.activities = value}
    get activities(){return this._state.activities}

    getTotalExpensesByQuantity(quantity) {
        const activityPrices = this.activities.map(x=>
            x.getTotalExpensesByQuantity(quantity))
        return activityPrices.reduce((a,b)=> a+b, 0)
    }
}

class Activity {
    constructor(name, expenses) {
        this._state = reactive({
            name, expenses
        })
    }

    set name(value){this._state.name = value}
    get name(){return this._state.name}

    set expenses(value){this._state.expenses = value}
    get expenses(){return this._state.expenses}

    getTotalExpensesByQuantity(quantity) {
        const expensesPrices = this.expenses.map(x=>
            x.getEstimatePriceByQuantity(quantity));
        return expensesPrices.reduce((a,b)=> a+b, 0);
    }
}

class Expense {
    constructor(name, type, rate, estimates) {
        this._state = reactive({
            name, type, rate, estimates
        })
    }

    set name(value){this._state.name = value}
    get name(){return this._state.name}

    set type(value){this._state.type = value}
    get type(){return this._state.type}

    set rate(value){this._state.rate = value}
    get rate(){return this._state.rate}

    set estimates(value){this._state.estimates = value}
    get estimates(){return this._state.estimates}  

    getEstimatePriceByQuantity(quantity) {
        const estimate = this.estimates.find(x=>x.itemQuantity == quantity);
        return (estimate.estimate || 1) * this.rate;
    } 
}

class ExpenseEstimate {
    constructor(itemQuantity, estimate){
        this._state = reactive({
            itemQuantity, estimate
        })
    }

    set itemQuantity(value){this._state.itemQuantity = value}
    get itemQuantity(){return this._state.itemQuantity}

    set estimate(value){this._state.estimate = value}
    get estimate(){return this._state.estimate}
}

export default {
    components: {
        Page, Button, Section, DeleteRecordDialog, DescriptionList, DescriptionItem
    },
    setup() {
        const currency = inject('currency').abbreviation
        const state = reactive({
            isProcessing: false,
            meta: {
                quantitiesColumnLength: computed(()=> Math.max(state.data.quantities.length, 1)),
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
                    }),
                    services: computed(()=> {
                        let estimates = state.data.quantities.map(x=> {
                            const servicesPrices = state.data.services.map(y=>
                                y.getTotalExpensesByQuantity(x));
                            return {
                                quantity: x,
                                price: servicesPrices.reduce((a,b)=>a+b, 0)
                            }
                        });
                        return estimates;
                    })
                }
            },
            data: {
                estimateCode: 'CE-1234',
                templateCode: 'PT-9876',
                templateName: 'Carbonless Form',
                templateDescription: '8.5x11" Carbonless Form (White, Yellow, Blue)',
                quantities: [100, 200, 300],
                billOfMaterials: [],
                services: []
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
                let price = 0;
                if (quantity > 0){
                    const material = state.meta.totals.materials.find(x=>x.quantity == quantity);
                    if (material) price = material.price;
                }
                return formatMoney(price);
            },
            getServicePriceByQuantity: (quantity=0) => {
                let price = 0;
                if (quantity > 0) {
                    const service = state.meta.totals.services.find(x=>x.quantity == quantity);
                    if (service) price = service.price;
                }
                return formatMoney(price);
            } 
        });

        const formatMoney = (amount)=> {
            if (amount != null)
                return formatCurrency(amount, currency)
            else return ''
        }

        const initializeBillOfMaterials = ()=> {
            const mockData = [
                {name: 'Generic Carbonless White 32x24inch', 
                rate: 30.00, 
                uom: 'sheet', 
                spoilageRate: 10, isExpanded: false,
                estimates: [
                {itemQuantity: 100, 
                    estimatedMaterialQuantity: 300,
                    spoilageMaterialQuantity: 30,
                    totalMaterialQuantity: 300},
                {itemQuantity: 200, 
                    estimatedMaterialQuantity: 600,
                    spoilageMaterialQuantity: 60,
                    totalMaterialQuantity: 600},
                {itemQuantity: 300, 
                    estimatedMaterialQuantity: 900,
                    spoilageMaterialQuantity: 90,
                    totalMaterialQuantity: 900}
                ]},
                {name: 'Carbonless Blue 32x24', 
                rate: 30.00, 
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
            ];
            mockData.forEach(data => {
                const estimates = data.estimates.map(x=> 
                    new MaterialEstimate(
                        x.itemQuantity, x.estimatedMaterialQuantity,
                        x.spoilageMaterialQuantity));
                const material = new Material(data.name, data.rate, 
                    data.uom, data.spoilageRate, estimates, currency);
                state.data.billOfMaterials.push(material); 
            })
        }

        const initializeServices = ()=> {
            const mockData = [
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

            mockData.forEach(a=>{
                const operations = a.operations.map(b=> {
                    const activities = b.activities.map(c => {
                        const expenses = c.expenses.map(d => {
                            const estimates = d.estimates.map(e =>
                                new ExpenseEstimate(e.itemQuantity, e.estimate));
                            return new Expense(d.name, d.type, d.rate, estimates);
                        })
                        return new Activity(c.name, expenses);
                    })
                    return new Operation(b.name, activities);
                });
                const service = new Service(a.name, a.uom, operations);
                state.data.services.push(service);
            })
        }

        onBeforeMount(()=> {
            initializeBillOfMaterials();
            initializeServices();
        })

        return {
            state,
            formatQuantity,
            formatMoney
        }
    }
    
}
</script>