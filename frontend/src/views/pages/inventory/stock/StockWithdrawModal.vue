<template>
    <Modal heading="Withdraw Request" :is-open="$props.isOpen"
        @toggle="(value)=> $emit('toggle', value)">
        <Section>
            <div class="grid md:grid-cols-4 md:gap-4">
                <dt class="text-lg mb-1">
                    <p class="font-semibold">Summary</p>
                </dt>
                <dd class="md:col-span-3 text- mt-1">
                    <p class="text-sm">Would you like to withdraw
                        <span class="font-bold">
                            {{formatQuantity($props.data.total,
                                $props.data.unit.name, $props.data.unit.plural)}}
                        </span>?
                    </p>
                    <Table :headers="['Brand Name', 
                        `Price / ${$props.data.unit.name}`, 'Withdraw Qty']">
                        <Row v-for="(stock, key) in $props.data.selected" :key="key">
                            <Cell label="Brand Name">{{stock.brandName}}</Cell>
                            <Cell label="Price">{{formatCurrency(stock.price)}}</Cell>
                            <Cell label="Withdraw Qty">
                                {{formatQuantity(stock.quantity, 
                                    $props.data.unit.name, $props.data.unit.plural)}}
                            </Cell>
                        </Row>
                    </Table>
                </dd>
            </div>
        </Section>
    </Modal>
</template>

<script>
import Modal from '@/components/Modal.vue';
import Section from '@/components/Section.vue';
import Table from '@/components/Table.vue'
import Row from '@/components/Row.vue'
import Cell from '@/components/Cell.vue'

import {inject} from 'vue'
import {formatMoney, formatQuantity} from '@/utils/format.js'

export default {
    components: {
        Modal, Section, Table, Row, Cell
    },
    props: {
        isOpen: Boolean,
        data: Object
    },
    setup() {
        const currency = inject('currency').abbreviation
        const formatCurrency = (amount)=> (
            amount != null ? formatMoney(amount, currency) : '')

        return {
            formatCurrency, formatQuantity
        }
    }
}
</script>