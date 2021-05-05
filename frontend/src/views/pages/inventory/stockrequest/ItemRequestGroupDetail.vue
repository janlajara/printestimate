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
        <Section heading="Item Request List">
            <ItemRequestModal 
                :is-open="detail.itemModal.isOpen"
                :item-request-id="detail.itemModal.selected"
                @toggle="detail.itemModal.toggle" />
            <ItemRequestAllocateStockModal 
                :is-open="detail.stockModal.isOpen"
                :read-only="detail.stockModal.readOnly"
                :item-request-id="detail.stockModal.selected"
                @toggle="detail.stockModal.toggle" />
            <ItemRequestUpdateStatusDialog 
                :data="detail.dialog.data"
                :on-after-execute="retrieveDetail"
                :is-open="detail.dialog.isOpen"
                @toggle="detail.dialog.toggle"/>
            <Button icon="add" color="tertiary"
                :action="()=>detail.itemModal.toggle(true)">Add Item</Button>
            <Table :headers="['Item', 'Status', 'Quantity', '']"
                :loader="detail.isProcessing">
                <Row v-for="(r, i) in detail.data.itemRequests" :key="i">
                    <Cell label="Item">{{r.itemName}}</Cell>
                    <Cell label="Status">
                        <ButtonOptions v-if="r.statusChoices.length > 0"
                            icon="expand_more" :label="r.status"> 
                            <ButtonOption v-for="(choice, key) in r.statusChoices" :key="key"
                                @click="()=>detail.dialog.select(r.id, choice)">
                                {{choice.label}}
                            </ButtonOption>
                        </ButtonOptions>
                        <span v-else class="font-bold">
                            {{r.status}}
                        </span>
                    </Cell>
                    <Cell label="Quantity">
                        <div class="cursor-pointer hover:text-secondary"
                            @click="()=>detail.stockModal.select(r.id, r.status)">
                            {{r.quantityStocked}} / {{r.quantityNeededFormatted}}
                            <span class="material-icons text-sm px-2 inline-block align-middle">
                                library_add</span>
                        </div>
                    </Cell>
                    <Cell class="px-0">
                        <div class="w-full flex justify-end">
                            <Button class="my-auto" icon="edit"
                                :disabled="['Approved', 'Partially Fulfilled', 'Fulfilled']
                                    .includes(r.status)"/>
                            <Button class="my-auto" icon="delete"
                                :disabled="['Approved', 'Partially Fulfilled', 'Fulfilled']
                                    .includes(r.status)"/>
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
import ItemRequestModal from '@/views/pages/inventory/stockrequest/ItemRequestModal.vue';

import {watch, reactive, onBeforeMount} from 'vue'
import {useRoute} from 'vue-router'
import {ItemRequestGroupApi} from '@/utils/apis.js'
import {reference} from '@/utils/format.js'

export default {
    components: {
        Page, Section, Button, ButtonOptions, ButtonOption, Table, Row, Cell, 
        DescriptionItem, DescriptionList, ItemRequestAllocateStockModal, 
        ItemRequestUpdateStatusDialog, ItemRequestModal
    },
    emits: ['toggle'],
    setup() {
        const route = useRoute()
        const detail = reactive({
            id: route.params.id,
            data: {},
            stockModal: {
                selected: null,
                isOpen: false,
                readOnly: true,
                toggle: value => {
                    detail.stockModal.isOpen = value;
                    if (!detail.stockModal.isOpen) retrieveDetail();
                },
                select: (id, status) => {
                    detail.stockModal.selected = id;
                    detail.stockModal.readOnly = 
                        !['Approved', 'Partially Fulfilled'].includes(status)
                    detail.stockModal.toggle(true);
                }
            },
            itemModal: {
                selected: null,
                isOpen: false,
                toggle: value => {
                    detail.itemModal.isOpen = value;
                    //if (!detail.itemModal.isOpen) retrieveDetail();
                },
                select: (id) => {
                    detail.itemModal.selected = id;
                    detail.itemModal.toggle(true);
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