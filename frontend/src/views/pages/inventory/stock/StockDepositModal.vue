<template>
    <Modal heading="Deposit Stock" :is-open="$props.isOpen"
        @toggle="(value)=> $emit('toggle', value)"
        :buttons="[{color: 'primary', icon:'download', text:'Deposit',
                    action:()=>stock.deposit(), disabled: stock.isProcessing},]">
        <Section class="grid md:grid-cols-4 md:gap-4">
            <InputSelect name="Deposit By" required
                @input="(value)=>stock.data.depositBy = value"
                :options="Object.entries($props.data.units).map((entry)=>({
                    value: entry[1].value, label: entry[1].name,
                    isSelected: entry[1].value == stock.data.depositBy
                }))"/>
            <InputText type="text" name="Brand Name" class="md:col-span-2"
                @input="(value)=>stock.data.brandName = value"
                :value="stock.data.brandName"/>
            <InputCheckbox label="Unbounded stock" 
                @input="(value)=> stock.data.unbounded = value"
                :value="stock.data.unbounded"/>
        </Section>
        <Section class="grid md:grid-cols-4 md:gap-4">
            <InputText
                type="number" required
                :name="(stock.uom.isAlt)?
                    `${$props.data.units.base.plural} per ${$props.data.units.alternate.name}`:
                    `${$props.data.units.base.name} Quantity`" 
                @input="(value)=>stock.data.baseQuantity = value"
                :value="stock.data.baseQuantity"/> 
            <InputText v-if="stock.uom.isAlt"
                type="number" required :disabled="stock.data.unbounded"
                :name="`${$props.data.units.alternate.name} Quantity`" 
                @input="(value)=>stock.data.alternateQuantity = value"
                :value="stock.data.alternateQuantity"/> 
            <InputText type="decimal"
                    :prefix="currency.symbol"
                    :name="`Price per ${stock.uom.target.name}`" 
                    @input="(value)=>stock.data.price = value"
                    :value="stock.data.price"/>
        </Section>
        <div class="grid md:grid-cols-4 md:gap-4">
            <dt class="text-lg mb-1 font-semibold">Summary</dt>
            <dd class="md:col-span-3 text-sm">
                <p class="my-2">
                    Note : This creates <span class="font-bold">{{stock.data.depositCount}} Stock 
                    {{stock.data.depositCount == 1 ? 'record' : 'records'}}</span>.</p>
                <p class="pb-2">
                    <span>Total {{$props.data.units.base.name}} Quantity : </span>
                    <span class="font-bold">{{stock.data.totalQuantityFormatted}}</span>
                    <span class="text-gray-400" v-if="stock.uom.isAlt && stock.data.alternateQuantity > 0">
                        {{` (${stock.data.baseFormatted} x ${stock.data.alternateFormatted}) `}}</span>                  
                </p>
                <p class="pb-2" v-if="stock.data.price > 0">
                    <span>Total Price : </span>
                    <span class="font-bold">{{stock.data.totalPriceFormatted}}</span>
                    <span class="text-gray-400">
                        {{` (${stock.uom.isAlt ? stock.data.alternateFormatted : stock.data.baseFormatted} x 
                            ${stock.data.priceFormatted})`}}
                    </span>
                </p>
                <p class="pb-2" v-if="stock.data.price > 0 && stock.uom.isAlt">
                    <span>Price per {{$props.data.units.base.name}} : </span>
                    <span class="font-bold">{{stock.data.pricePerBaseFormatted}}</span>
                    <span class="text-gray-400">
                        {{` (${stock.data.baseFormatted} / ${stock.data.priceFormatted})`}}</span>
                </p>
            </dd>
        </div>
    </Modal>
</template>

<script>
import Modal from '@/components/Modal.vue';
import Section from '@/components/Section.vue';
import InputText from '@/components/InputText.vue';
import InputSelect from '@/components/InputSelect.vue';
import InputCheckbox from '@/components/InputCheckbox.vue';
import {formatQuantity, formatMoney} from '@/utils/format.js';

import {reactive, computed, watch, inject} from 'vue';

export default {
    components: {
        Modal, Section, InputText, InputSelect, InputCheckbox
    },
    props: {
        isOpen: {
            type: Boolean,
            required: true
        },
        data: {
            type: Object,
            required: true
        }
    },
    emits: ['toggle'],
    setup(props) {
        const currency = inject('currency')
        const stock = reactive({
            uom: {
                base: {}, 
                alternate: {},
                target: computed(()=> {
                    let unit = props.data.units.base;
                    if (stock.uom.isAlt) 
                        unit = props.data.units.alternate;
                    return unit;
                }),
                isAlt: computed(()=> 
                    props.data.units.alternate.value == stock.data.depositBy),
            },
            data: {
                brandName: null,
                depositBy: null,
                unbounded: true,
                price: 0,
                priceFormatted: computed(()=> {
                    const price = stock.data.price? stock.data.price : 0;
                    return formatMoney(price, currency.abbreviation);
                }),
                baseQuantity: 0,
                baseFormatted: computed(()=> {
                    const qty = (stock.data.baseQuantity)?
                        stock.data.baseQuantity : 0;
                    const baseUnit = props.data.units.base;
                    return formatQuantity(qty, baseUnit.name, baseUnit.plural)
                }),
                alternateQuantity: 1,
                alternateFormatted: computed(()=> {
                    const qty = (stock.data.alternateQuantity)?
                        stock.data.alternateQuantity : 0;
                    const altUnit = props.data.units.alternate;
                    return formatQuantity(qty, altUnit.name, altUnit.plural)
                }),
                totalQuantity: computed(()=> {
                    let total = stock.data.baseQuantity ? 
                        stock.data.baseQuantity : 0;
                    const altQty = stock.data.alternateQuantity ? 
                        stock.data.alternateQuantity : 1;
                    if (stock.uom.isAlt) {
                        total =  altQty * stock.data.baseQuantity;
                    }
                    return total ? total : 0;
                }),
                totalQuantityFormatted: computed(()=> {
                    const baseUnit = props.data.units.base;
                    return formatQuantity(stock.data.totalQuantity, baseUnit.name, baseUnit.plural)
                }),
                totalPrice: computed(()=> {
                    const baseQty = stock.data.baseQuantity ? stock.data.baseQuantity : 0;
                    const price = stock.data.price ? stock.data.price : 0;
                    if (stock.uom.isAlt) {
                        const altQ = stock.data.alternateQuantity ? stock.data.alternateQuantity : 0;
                        return price * altQ;
                    } 
                    return price * baseQty;
                }),
                totalPriceFormatted: computed(()=> 
                    formatMoney(stock.data.totalPrice, currency.abbreviation)),
                pricePerBase: computed(()=> {
                    const baseQty = stock.data.baseQuantity ? stock.data.baseQuantity : 0;
                    const price = stock.data.price ? stock.data.price : 0;
                    return price > 0 ? baseQty / price : 0;
                }),
                pricePerBaseFormatted: computed(()=> {
                    return stock.data.pricePerBase > 0 ?
                        formatMoney(stock.data.pricePerBase, currency.abbreviation):
                        'N/A';
                }),
                depositCount: computed(()=> {
                    let count = 0;
                    if (stock.uom.isAlt) count = stock.data.alternateQuantity;
                    else count = (stock.data.baseQuantity > 0) ? 1 : 0;

                    return count; 
                }),
            },
            isProcessing: false,
            deposit: ()=> {
                let price = stock.data.price;
                if (!stock.data.unbounded && !stock.uom.isAlt)
                    price = stock.data.baseQuantity * stock.data.price;

                const data = {
                    brand_name: stock.data.brandName,
                    base_quantity: stock.data.baseQuantity,
                    price: price,
                    alt_quantity: stock.uom.isAlt ? 
                        stock.data.alternateQuantity : 1,
                    unbounded: stock.data.unbounded,
                }
                console.log(data);
            }
        });

        watch(()=> props.data.units, ()=> { 
            stock.uom.base = props.data.units;
            stock.uom.alternate = props.data.alternate; 
        });
        watch(()=> stock.data.depositBy, ()=> {
            stock.data.price = 0;
            stock.data.unbounded = !stock.uom.isAlt;
        });
        watch(()=> stock.data.unbounded, ()=> {
            stock.data.alternateQuantity = 1;
        });

        return {
            stock,
            currency
        }
    }
}
</script>