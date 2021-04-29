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
            <ItemRequestAllocateStockModal :is-open="detail.modal.isOpen"
                :item-request-id="detail.modal.selected"
                @toggle="detail.modal.toggle" />
            <ItemRequestUpdateStatusDialog 
                :data="detail.dialog.data"
                :on-after-execute="retrieveDetail"
                :is-open="detail.dialog.isOpen"
                @toggle="detail.dialog.toggle"/>
            <Table :headers="['Item', 'Status', 'Quantity', '']"
                :loader="detail.isProcessing">
                <Row v-for="(r, i) in detail.data.itemRequests" :key="i">
                    <Cell label="Item">{{r.itemName}}</Cell>
                    <Cell label="Status">
                        <ButtonOptions icon="expand_more" :label="r.status"> 
                            <ButtonOption class="border-b border-gray-400 border-opacity-30"
                                v-if="r.status == 'Approved'"
                                @click="()=>detail.modal.select(r.id)">
                                Allocate Stocks
                            </ButtonOption>
                            <ButtonOption v-for="(choice, key) in r.statusChoices" :key="key"
                                @click="()=>detail.dialog.select(r.id, choice)">
                                {{choice.label}}
                            </ButtonOption>
                        </ButtonOptions>
                    </Cell>
                    <Cell label="Quantity">
                        {{r.quantityStocked}} / {{r.quantityNeededFormatted}}
                    </Cell>
                    <Cell class="px-0">
                        <div class="w-full flex justify-end">
                            <Button class="my-auto" icon="edit"
                                :disabled="['Approved', 'Fulfilled'].includes(r.status)"/>
                            <Button class="my-auto" icon="delete"
                                :disabled="['Approved', 'Fulfilled'].includes(r.status)"/>
                        </div>
                    </Cell>
                </Row>
            </Table>
        </Section>
    </Page>
</template>
<script>
import Page from '@/components/Page.vue';
import Section from '@/components/Section.vue';
import Button from '@/components/Button.vue';
import ButtonOptions from '@/components/ButtonOptions.vue';
import ButtonOption from '@/components/ButtonOption.vue';
import Table from '@/components/Table.vue';
import Row from '@/components/Row.vue';
import Cell from '@/components/Cell.vue';
import DescriptionItem from '@/components/DescriptionItem.vue';
import DescriptionList from '@/components/DescriptionList.vue';
import ItemRequestAllocateStockModal from '@/views/pages/inventory/stockrequest/ItemRequestAllocateStockModal.vue';
import ItemRequestUpdateStatusDialog from '@/views/pages/inventory/stockrequest/ItemRequestUpdateStatusDialog.vue';

import {watch, reactive, onBeforeMount} from 'vue'
import {useRoute} from 'vue-router'
import {ItemRequestGroupApi} from '@/utils/apis.js'
import {reference} from '@/utils/format.js'

export default {
    components: {
        Page, Section, Button, ButtonOptions, ButtonOption, Table, Row, Cell, 
        DescriptionItem, DescriptionList, ItemRequestAllocateStockModal, ItemRequestUpdateStatusDialog
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
                toggle: value => {
                    detail.modal.isOpen = value;
                    if (!detail.modal.isOpen) retrieveDetail();
                },
                select: id => {
                    detail.modal.selected = id;
                    detail.modal.toggle(true);
                }
            },
            dialog: {
                data: {
                    id: null,
                    choice: null
                },
                isOpen: false,
                toggle: value => {
                    detail.dialog.isOpen = value;
                },
                select: (id, choice) => {
                    detail.dialog.data = {
                        id, choice};
                    detail.dialog.toggle(true);
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
                            statusChoices: r.status_choices,
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
                    };
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
            detail, retrieveDetail
        }
    }
}
</script>