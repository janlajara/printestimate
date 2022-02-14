<template>
    <div>
        <!-- Table Rows for Services -->
        <div class="text-primary-dark font-bold">
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
                <div :class="`grid grid-cols-${state.meta.quantitiesColumnLength} gap-x-2 divide-x`"
                    v-show="!service.isExpanded">
                    <div v-for="(quantity, a) in state.paginate(state.data.quantities)" :key="a" class="grid">
                        <div class="flex text-xs my-auto">
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
            <div v-show="service.isExpanded">
                <!-- Service Breakdown Expandable -->
                <div v-for="(operation, x) in service.operations" :key="x"
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
                                        {{expense.rateLabel}}</span>    
                                </div>
                            </div>
                            <div :class="`grid grid-cols-${state.meta.quantitiesColumnLength} gap-x-2 divide-x`">
                                <div v-for="(estimate, a) in state.paginate(expense.estimates)" :key="a" class="grid">
                                    <div class="flex text-xs my-auto">
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
                <div class="border-t-2 border-dotted grid grid-cols-2 mb-4">
                    <div>
                    </div>
                    <div :class="`grid grid-cols-${state.meta.quantitiesColumnLength}`">
                        <div v-for="(quantity, y) in state.meta.displayedQuantities" :key="y" class="my-auto">
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
        </div>
        
        <!-- Total for all Services -->
        <div class="grid grid-cols-2">
            <div>
            </div>
            <div :class="`grid grid-cols-${state.meta.quantitiesColumnLength} gap-x-2 divide-x`">
                <div v-for="(quantity, x) in state.meta.displayedQuantities" :key="x">
                    <div class="text-xs flex py-1">
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
</template>
<script>
import {reactive, inject, computed, watch} from 'vue';
import {formatQuantity, formatMoney as formatCurrency} from '@/utils/format.js';

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
    constructor(name, type, rate, rateLabel, estimates) {
        this._state = reactive({
            name, type, rate, rateLabel, estimates
        })
    }

    set name(value){this._state.name = value}
    get name(){return this._state.name}

    set type(value){this._state.type = value}
    get type(){return this._state.type}

    set rate(value){this._state.rate = value}
    get rate(){return this._state.rate}

    set rateLabel(value){this._state.rateLabel = value}
    get rateLabel(){return this._state.rateLabel}

    set estimates(value){this._state.estimates = value}
    get estimates(){return this._state.estimates}  

    getEstimatePriceByQuantity(quantity) {
        const estimate = this.estimates.find(x=>x.itemQuantity == quantity);
        if (estimate) return (estimate.estimate || 1) * this.rate;
        else return 0;
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
    props: {
        quantities: Array,
        services: Array,
        quantityViewableOffset: {
            type: Number,
            default: 0
        },
        maxQuantityViewable: {
            type: Number,
            default: 2
        }
    },
    setup(props) {
        const currency = inject('currency').abbreviation;
        const state = reactive({
            meta: {
                quantitiesColumnLength: computed(()=> 
                    Math.min(state.data.quantities.length, 
                        props.maxQuantityViewable)
                ),
                totals: {
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
                },
                displayedQuantities: computed(()=>
                    state.paginate(state.data.quantities))
            },
            data: {
                quantities: computed(()=> props.quantities),
                services: []
            },
            getServicePriceByQuantity: (quantity=0) => {
                let price = 0; 
                if (quantity > 0) {
                    const service = state.meta.totals.services.find(x=>x.quantity == quantity);
                    if (service) price = service.price;
                }
                return formatMoney(price);
            },
            paginate: (array) => {
                let spliced = [...array];
                if (array) spliced = spliced.splice(
                    props.quantityViewableOffset, 
                    state.meta.quantitiesColumnLength);
                return spliced;
            }
        });

        const formatMoney = (amount)=> {
            if (amount != null)
                return formatCurrency(amount, currency)
            else return ''
        }

        const initializeServices = ()=> {
            state.data.services = [];
            if (props.services) {
                props.services.forEach(a=>{
                    const operations = a.operations.map(b=> {
                        const activities = b.activities.map(c => {
                            const expenses = c.expenses.map(d => {
                                const estimates = d.estimates.map(e =>
                                    new ExpenseEstimate(e.itemQuantity, e.estimate));
                                return new Expense(d.name, d.type, d.rate, d.rateLabel, estimates);
                            })
                            return new Activity(c.name, expenses);
                        })
                        return new Operation(b.name, activities);
                    });
                    const service = new Service(a.name, a.uom, operations);
                    state.data.services.push(service);
                })
            }
        }

        watch(()=>props.services, initializeServices);

        return {
            state, formatMoney, formatQuantity
        }
    }
}
</script>