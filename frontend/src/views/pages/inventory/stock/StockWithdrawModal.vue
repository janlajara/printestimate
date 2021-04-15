<template>
    <Modal heading="Withdraw Request" :is-open="$props.isOpen"
        @toggle="(value)=> $emit('toggle', value)"
        :buttons="[{color: 'primary', icon:'upload', text:'Request',
                    action:()=>stock.withdraw(), disabled: stock.isProcessing},]">
        <Section heading="Details" class="grid md:grid-cols-4">
            <InputText type="text" name="Reason"
                        @input="(value)=>stock.data.reason = value"
                        :value="stock.data.reason"/>
        </Section>
        <Section heading="Summary" class="grid md:grid-cols-4 md:gap-4">
            <dd class="text-sm md:col-span-3 md:mt-3">
                <p class="text-sm">Would you like to withdraw
                    <span class="font-bold">
                        {{$props.data.total}}
                    </span>?
                </p>
                <Table :headers="['Brand Name', 
                    `Price / ${$props.data.unit}`, 'Withdraw Qty']">
                    <Row v-for="(s, key) in $props.data.selected" :key="key">
                        <Cell label="Brand Name">{{s.brandName}}</Cell>
                        <Cell label="Price">{{formatCurrency(s.price)}}</Cell>
                        <Cell label="Withdraw Qty">
                            {{s.quantityFormatted}}
                        </Cell>
                    </Row>
                </Table>
            </dd>
        </Section>
    </Modal>
</template>

<script>
import Modal from '@/components/Modal.vue';
import Section from '@/components/Section.vue';
import Table from '@/components/Table.vue'
import Row from '@/components/Row.vue'
import Cell from '@/components/Cell.vue'
import InputText from '@/components/InputText.vue';

import {inject, reactive, watch} from 'vue';
import {formatMoney} from '@/utils/format.js';
import {ItemApi} from '@/utils/apis.js';

export default {
    components: {
        Modal, Section, Table, Row, Cell, InputText
    },
    props: {
        isOpen: Boolean,
        data: Object,
        onAfterWithdraw: Function
    },
    setup(props, {emit}) {
        const currency = inject('currency').abbreviation
        const formatCurrency = (amount)=> (
            amount != null ? formatMoney(amount, currency) : '')
        const stock = reactive({
            data: {
                reason: null,
                stockRequests: []
            },
            isProcessing: false,
            withdraw: async ()=> {
                const itemId = props.data.itemId;
                if (itemId && stock.data.stockRequests) {
                    const request = {
                        reason: stock.data.reason,
                        stock_requests: stock.data.stockRequests.map(r=> ({
                            id: r.id, quantity: r.quantity    
                        }))};
                    stock.isProcessing = true;
                    const response = await ItemApi.requestStocks(itemId, request);
                    if (response && !response.error) {
                        emit('toggle', false);
                        if (props.onAfterWithdraw) props.onAfterWithdraw();
                    }
                    stock.isProcessing = false;
                }
            }
        })
        watch(()=> props.isOpen, ()=> {
            stock.data.reason = null;
        })
        watch (()=> props.data.selected, ()=> {
            if (props.data.selected) 
                stock.data.stockRequests = Array.from(props.data.selected);
        })

        return {
            formatCurrency, 
            stock
        }
    }
}
</script>