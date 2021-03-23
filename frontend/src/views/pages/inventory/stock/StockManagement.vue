<template>
    <Section heading="Stock Management" class="mt-12">
        <div class="flex">
            <Button icon="upload" color="secondary" class="mr-4">Withdraw</Button>
            <Button icon="download" color="secondary" class="mr-4"
                :action="()=> stock.deposit.isOpen = true">Deposit</Button>
            <StockDepositModal :is-open="stock.deposit.isOpen"
                :data="{units: {
                    base: $props.data.baseUom,
                    alternate: $props.data.altUom}}"
                @toggle="(value)=> stock.deposit.isOpen = value"/>
        </div>
        <DescriptionList class="grid-cols-2 md:grid-cols-4">
            <DescriptionItem name="Available" :value="$props.data.availableQuantityFormatted"/>
            <DescriptionItem name="On-hand" :value="$props.data.onhandQuantityFormatted"/>
            <DescriptionItem name="Average Price" :value="$props.data.averagePriceFormatted"/>
            <DescriptionItem name="Latest Price" :value="$props.data.latestPriceFormatted"/>
        </DescriptionList>
        <Tabs>
            <Tab title="On-hand">
            </Tab>
            <Tab title="Requests"></Tab>
            <Tab title="Incoming"></Tab>
            <Tab title="History"></Tab>
        </Tabs>
    </Section>
</template>

<script>
import Section from '@/components/Section.vue';
import DescriptionList from '@/components/DescriptionList.vue';
import DescriptionItem from '@/components/DescriptionItem.vue';
import Button from '@/components/Button.vue';
import Tabs from '@/components/Tabs.vue';
import Tab from '@/components/Tab.vue';
import StockDepositModal from '@/views/pages/inventory/stock/StockDepositModal.vue';

import {reactive} from 'vue';

export default {
    components: {
        Section, DescriptionList, DescriptionItem, Tabs, Tab, Button,
        StockDepositModal
    },
    props: {
        data: {
            type: Object,
            required: true
        }
    },
    setup() { 
        const stock = reactive({
            withdraw: {
                isOpen: false
            },
            deposit: {
                isOpen: false
            }
        });
        return {
            stock
        }
    }
}
</script>