<template>
    <Modal heading="Deposit Stock" :is-open="$props.isOpen"
        @toggle="(value)=> $emit('toggle', value)"
        :buttons="[{color: 'primary', icon:'download', text:'Deposit',
                    action:()=>stock.deposit(), disabled: stock.isProcessing},]">
        <Section heading="Details" class="grid md:grid-cols-4 md:gap-4">
            <div class="md:col-span-3 md:grid md:grid-cols-3 md:gap-4">
                <InputSelect name="Deposit By" required
                    @input="(value)=>stock.data.depositBy = value"
                    :options="Object.entries($props.data.units)
                        .filter( entry => entry[1] != null)
                        .map((entry)=>({
                            value: entry[1].id, label: entry[1].name,
                            isSelected: entry[1].id == stock.data.depositBy
                        }))"/>
                <InputText type="text" name="Brand Name" class="md:col-span-2"
                    @input="(value)=>stock.data.brandName = value"
                    :value="stock.data.brandName"/>
                <InputText
                    type="number" required
                    :name="(stock.uom.isAlt)?
                        `${stock.uom.base.plural_name} per ${stock.uom.alternate.name}`:
                        `${stock.uom.base.name} Quantity`" 
                    @input="(value)=>stock.data.baseQuantity = value"
                    :value="stock.data.baseQuantity"/> 
                <InputText v-if="stock.uom.isAlt"
                    type="number" required 
                    :name="`${stock.uom.alternate.name} Quantity`" 
                    @input="(value)=>stock.data.alternateQuantity = value"
                    :value="stock.data.alternateQuantity"/> 
                <InputText type="decimal" required
                        :prefix="currency.symbol"
                        :name="`Price per ${stock.uom.target.name}`" 
                        @input="(value)=>stock.data.price = value"
                        :value="stock.data.price"/>
                <InputCheckbox label="Unbounded stock" v-if="!stock.uom.isAlt"
                    @input="(value)=> stock.data.unbounded = value"
                    :value="stock.data.unbounded"/>
            </div>
        </Section>
        <Section heading="Summary" class="grid md:grid-cols-4 md:gap-4">
            <dd class="md:mt-2 md:col-span-3 text-sm">
                <p class="my-2">
                    Note : This creates <span class="font-bold">{{stock.data.depositCount}} Stock 
                    {{stock.data.depositCount == 1 ? 'record' : 'records'}}</span>.</p>
                <p class="pb-2">
                    <span>Total {{stock.uom.base.name}} Quantity : </span>
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
                    <span>Price per {{stock.uom.base.name}} : </span>
                    <span class="font-bold">{{stock.data.pricePerBaseFormatted}}</span>
                    <span class="text-gray-400">
                        {{` (${stock.data.baseFormatted} / ${stock.data.priceFormatted})`}}</span>
                </p>
            </dd>
        </Section>
    </Modal>
</template>

<script>
import Modal from '@/components/Modal.vue';
import Section from '@/components/Section.vue';
import InputText from '@/components/InputText.vue';
import InputSelect from '@/components/InputSelect.vue';
import InputCheckbox from '@/components/InputCheckbox.vue';
import {reactive, computed, watch, inject} from 'vue';

import {formatQuantity, formatMoney} from '@/utils/format.js';
import {ItemApi} from '@/utils/apis.js';

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
        },
        onAfterDeposit: Function
    },
    emits: ['toggle'],
    setup(props, {emit}) {
        const currency = inject('currency')
        const stock = reactive({
            uom: {
                base: {id: null, name: '', plural_name: ''},
                alternate: {id: null, name: '', plural_name: ''},
                target: computed(()=> {
                    let unit = stock.uom.base;
                    if (stock.uom.isAlt) 
                        unit = stock.uom.alternate;
                    return unit;
                }),
                isAlt: computed(()=> (
                    stock.uom.alternate && stock.uom.alternate.id != null ?
                        stock.uom.alternate.id == stock.data.depositBy :
                        false
                )),
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
                    const baseUnit = stock.uom.base; 
                    return formatQuantity(qty, baseUnit.abbrev, baseUnit.plural_abbrev)
                }),
                alternateQuantity: 1,
                alternateFormatted: computed(()=> {
                    const qty = (stock.data.alternateQuantity)?
                        stock.data.alternateQuantity : 0;
                    const altUnit = stock.uom.alternate;
                    return formatQuantity(qty, altUnit.abbrev, altUnit.plural_abbrev)
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
                    const baseUnit = stock.uom.base; 
                    return formatQuantity(stock.data.totalQuantity, baseUnit.abbrev, baseUnit.plural_abbrev)
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
            deposit: async ()=> {
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
                stock.isProcessing = true;
                const response = await ItemApi.depositStock(props.data.itemId, data)
                if (response && !response.error) {
                    emit('toggle', false);
                    if (props.onAfterDeposit) props.onAfterDeposit();
                }
                stock.isProcessing = false;
            }
        });

        watch(()=> props.isOpen, ()=> {
            stock.data.brandName = null;
            stock.data.depositBy = null;
            stock.data.unbounded = true;
            stock.data.price = 0;
            stock.data.baseQuantity = 0;
            stock.data.alternateQuantity = 1;
        })
        watch(()=> props.data.units, ()=> { 
            if (props.data.units.base) stock.uom.base = props.data.units.base;
            if (props.data.units.alternate) stock.uom.alternate = props.data.units.alternate;
        })
        watch(()=> stock.data.depositBy, ()=> {
            stock.data.price = 0;
            stock.data.unbounded = !stock.uom.isAlt;
        });

        return {
            stock,
            currency
        }
    }
}
</script>