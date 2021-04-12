<template>
    <Page :title="`Request : ${detail.data.code ? detail.data.code : ''}`">
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
        <Section heading="Item Request List" class="mt-12">
            <ItemRequestModal :is-open="detail.modal.isOpen"
                :item-request-id="detail.modal.selected"
                @toggle="detail.modal.toggle" />
            <Table :headers="['Item', 'Quantity Allocated', 'Status', 'Approved?']"
                :loader="detail.isProcessing">
                <Row v-for="(r, i) in detail.data.itemRequests" :key="i"
                    clickable @click="()=> detail.modal.select(r.id)">
                    <Cell label="Item">{{r.itemName}}</Cell>
                    <Cell label="Quantity Allocated">
                        {{r.quantityStocked}} / {{r.quantityNeededFormatted}}
                    </Cell>
                    <Cell label="Status">
                        {{r.status}}
                    </Cell>
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
import ItemRequestModal from '@/views/pages/inventory/stockrequest/ItemRequestModal.vue';

import {watch, reactive, onBeforeMount} from 'vue'
import {useRoute} from 'vue-router'
import {ItemRequestGroupApi} from '@/utils/apis.js'
import {reference} from '@/utils/format.js'

export default {
    components: {
        Page, Section, Button, Table, Row, Cell, 
        DescriptionItem, DescriptionList, ItemRequestModal
    },
    emits: ['toggle'],
    setup() {
        const route = useRoute()
        const detail = reactive({
            id: route.params.id,
            data: {},
            modal: {
                selected: null,
                isOpen: false,
                toggle: value => detail.modal.isOpen = value,
                select: id => {
                    detail.modal.selected = id;
                    detail.modal.toggle(true);
                }
            },
            isProcessing: false
        })
        const retrieveDetail = async ()=> {
            detail.isProcessing = true;
            if (detail.id) {
                const response = await ItemRequestGroupApi.retrieveItemRequestGroup(detail.id)
                if (response) {
                    detail.data = {
                        id: response.id,
                        code: reference.formatId(response.id, reference.mrs),
                        status: response.status,
                        finished: response.finished,
                        reason: response.reason,
                        created: response.created_at,
                        itemRequests: response.item_requests.map(r => ({
                            id: r.id,
                            status: r.status,
                            itemId: r.item_id,
                            itemName: r.item_name,
                            baseUom: r.item_base_uom,
                            isFullyAllocated: r.is_fully_allocated,
                            allocationRate: r.allocation_rate,
                            missingAllocation: r.missing_allocation,
                            missingAllocationFormatted: r.missing_allocation_formatted,
                            quantityStocked: r.quantity_stocked,
                            quantityStockedFormatted: r.quantity_stocked_formatted,
                            quantityNeeded: r.quantity_needed,
                            quantityNeededFormatted: r.quantity_needed_formatted,
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