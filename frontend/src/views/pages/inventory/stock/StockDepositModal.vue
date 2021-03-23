<template>
    <Modal heading="Deposit Stock" :is-open="$props.isOpen"
        @toggle="(value)=> $emit('toggle', value)"
        :buttons="[{color: 'primary', icon:'download', text:'Deposit',
                    action:()=>stock.deposit(), disabled: stock.isProcessing},]">
        <Section class="grid md:grid-cols-4 md:gap-4">
            <InputSelect name="Deposit By" required
                @input="(value)=>stock.data.depositBy = value"
                :options="Object.entries($props.data.units).map((entry, index)=>({
                    value: entry[1].value, label: entry[1].name,
                    isSelected: index == 0
                }))"/>
            <InputText type="text" name="Brand Name" class="md:col-span-3"
                @input="(value)=>stock.data.brandName = value"
                :value="stock.data.brandName"/>
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
                type="number" required
                :name="`${$props.data.units.alternate.name} Quantity`" 
                @input="(value)=>stock.data.alternateQuantity = value"
                :value="stock.data.alternateQuantity"/> 
            <InputText type="decimal" required
                    postfix="PHP"
                    :name="`Price per ${stock.uom.target.name}`" 
                    @input="(value)=>stock.data.price = value"
                    :value="stock.data.price"/>
        </Section>
        <div class="grid md:grid-cols-4 md:gap-4">
            <dt class="text-lg mb-1 font-semibold">Summary</dt>
            <dd class="md:col-span-3 text-sm mt-2">
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

import {reactive, computed, watch} from 'vue';

export default {
    components: {
        Modal, Section, InputText, InputSelect
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
                price: 0,
                priceFormatted: computed(()=> {
                    const price = stock.data.price? stock.data.price : 0;
                    return Number(price).toLocaleString() + ' PHP';
                }),
                baseQuantity: 0,
                baseFormatted: computed(()=> {
                    const qty = (stock.data.baseQuantity)?
                        stock.data.baseQuantity : 0;
                    const unit = (stock.data.baseQuantity == 1)?
                        props.data.units.base.name:
                        props.data.units.base.plural;
                    return `${Number(qty).toLocaleString()} ${unit}`;
                }),
                alternateQuantity: 0,
                alternateFormatted: computed(()=> {
                    const qty = (stock.data.alternateQuantity)?
                        stock.data.alternateQuantity : 0;
                    const unit = (stock.data.alternateQuantity == 1)?
                        props.data.units.alternate.name:
                        props.data.units.alternate.plural;
                    return `${Number(qty).toLocaleString()} ${unit}`;
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
                    const unit = (stock.data.totalQuantity == 1)?
                        props.data.units.base.name : props.data.units.base.plural; 
                    return `${Number(stock.data.totalQuantity).toLocaleString()} 
                            ${unit}`;
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
                totalPriceFormatted: computed(()=> Number(stock.data.totalPrice).toLocaleString() + ' PHP'),
                pricePerBase: computed(()=> {
                    const baseQty = stock.data.baseQuantity ? stock.data.baseQuantity : 0;
                    const price = stock.data.price ? stock.data.price : 0;
                    return price > 0 ? baseQty / price : 0;
                }),
                pricePerBaseFormatted: computed(()=> {
                    return stock.data.pricePerBase > 0 ?
                        Number(stock.data.pricePerBase).toLocaleString() + ' PHP':
                        'N/A';
                })
            },
            isProcessing: false,
            deposit: ()=> {
                console.log('deposit')
            }
        });

        watch(()=> props.data.units, ()=> { 
            stock.uom.base = props.data.units;
            stock.uom.alternate = props.data.alternate; 
        });
        watch(()=> stock.data.depositBy, ()=> {
            stock.data.price = 0;
        });

        return {
            stock
        }
    }
}
</script>