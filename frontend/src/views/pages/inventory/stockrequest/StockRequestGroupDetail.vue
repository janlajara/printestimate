<template>
    <Page :title="'Request : ' + detail.mrsId">
        <hr class="my-4"/>
        <div class="flex">
            <Button color="secondary" icon="arrow_back"
                :action="()=>$router.go(-1)">Go Back</Button>
        </div> 
        <Section>
            <DescriptionList class="grid-cols-2 md:grid-cols-4">
                <DescriptionItem :loader="detail.isProcessing"
                    name="Status" :value="detail.data.status"/>
                <DescriptionItem :loader="detail.isProcessing"
                    name="Reason" :value="detail.data.reason"/>
                <DescriptionItem :loader="detail.isProcessing"
                    name="Date Created" :value="detail.data.created"/>
            </DescriptionList>
        </Section>
        <Section heading="Stock Request Details" class="mt-12">
            <Table :headers="['Item', 'Brand', 'Quantity', 'Status', 'Approved?']"
                :loader="detail.isProcessing">
                <Row v-for="(r, i) in detail.data.stockRequests" :key="i">
                    <Cell label="Item">{{r.item}}</Cell>
                    <Cell label="Brand">{{r.brand}}</Cell>
                    <Cell label="Quantity">{{r.quantityFormatted}}</Cell>
                    <Cell label="Status">{{r.status}}</Cell>
                    <Cell label="Approved?"></Cell>
                </Row>
            </Table>
        </Section>
    </Page>
</template>
<script>
import Page from '@/components/Page.vue';
import Section from '@/components/Section.vue';
import Button from '@/components/Button.vue';
import Table from '@/components/Table.vue';
import Row from '@/components/Row.vue';
import Cell from '@/components/Cell.vue';
import DescriptionItem from '@/components/DescriptionItem.vue';
import DescriptionList from '@/components/DescriptionList.vue';

import {computed, watch, reactive, onBeforeMount} from 'vue'
import {useRoute} from 'vue-router'
import {StockRequestApi} from '@/utils/apis.js'
import {reference} from '@/utils/format.js'

export default {
    components: {
        Page, Section, Button, Table, Row, Cell, DescriptionItem, DescriptionList
    },
    emits: ['toggle'],
    setup() {
        const route = useRoute()
        const detail = reactive({
            id: route.params.id,
            mrsId: computed(()=> 
                reference.formatId(detail.id, reference.stockRequestGroup)
            ),
            data: {},
            isProcessing: false
        })
        const retrieveDetail = async ()=> {
            detail.isProcessing = true;
            if (detail.id) {
                const response = await StockRequestApi.retrieveStockRequestGroup(detail.id)
                if (response) {
                    detail.data = {
                        status: response.status,
                        reason: response.reason,
                        created: response.created_at,
                        stockRequests: response.stock_requests.map(r => ({
                            id: r.id,
                            code: reference.formatId(r.id, reference.stock),
                            item: r.item,
                            brand: r.stock.brand_name,
                            quantity: r.stock_unit.quantity,
                            quantityFormatted: r.stock_unit.quantity_formatted,
                            status: r.status,
                            created: r.created
                        }))
                    }
                } 
            }
            detail.isProcessing =false;
        }
        onBeforeMount(retrieveDetail);
        watch(()=> route.params.id, ()=> {
            const id = route.params.id;
            if (id != null && !isNaN(id)) {
                detail.id = parseInt(id);
                retrieveDetail();
            }
        });

        return {
            detail
        }
    }
}
</script>