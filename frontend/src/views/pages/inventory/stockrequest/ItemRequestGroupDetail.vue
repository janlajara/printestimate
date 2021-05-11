<template>
    <Page :title="`Request : ${detail.data.code ? detail.data.code : ''}`">
        <hr class="my-4"/>
        <div class="flex gap-4">
            <ItemRequestGroupModal 
                :data="detail.itemRequestGroup.editModal.data"
                :is-open="detail.itemRequestGroup.editModal.isOpen" 
                :on-after-save="retrieveDetail"
                @toggle="detail.itemRequestGroup.editModal.toggle"/>
            <Button color="secondary" icon="arrow_back"
                :action="()=>$router.go(-1)">Go Back</Button>
            <Button class="my-auto" icon="edit"
                @click="detail.itemRequestGroup.editModal.edit"/>
            <Button class="my-auto" icon="delete"/>
        </div> 
        <Section>
            <DescriptionList class="grid-cols-2 md:grid-cols-4">
                <DescriptionItem :loader="detail.isProcessing" 
                    name="Status" :value="detail.data.status"/>
                <DescriptionItem :loader="detail.isProcessing"
                    name="Date Created" :value="detail.data.created"/>
                <DescriptionItem :loader="detail.isProcessing"
                    name="Reason" :value="detail.data.reason"
                    class="col-span-2"/>
            </DescriptionList>
        </Section>
        <Section heading="Item Request List">
            <ItemRequestModal 
                :is-open="detail.itemRequest.itemModal.isOpen"
                :item-request-group-id="parseInt(detail.id)"
                :item-request-id="detail.itemRequest.itemModal.selected"
                :on-after-add="retrieveDetail"
                @toggle="detail.itemRequest.itemModal.toggle" />
            <ItemRequestAllocateStockModal 
                :is-open="detail.itemRequest.stockModal.isOpen"
                :read-only="detail.itemRequest.stockModal.readOnly"
                :item-request-id="detail.itemRequest.stockModal.selected"
                :on-after-add="retrieveDetail"
                @toggle="detail.itemRequest.stockModal.toggle" />
            <ItemRequestUpdateStatusDialog 
                :data="detail.itemRequest.statusDialog.data"
                :on-after-execute="retrieveDetail"
                :is-open="detail.itemRequest.statusDialog.isOpen"
                @toggle="detail.itemRequest.statusDialog.toggle"/>
            <ItemRequestDeleteDialog
                :data="detail.itemRequest.deleteDialog.data"
                :item-request-id="detail.itemRequest.deleteDialog.itemRequestId"
                :on-after-execute="retrieveDetail"
                :is-open="detail.itemRequest.deleteDialog.isOpen"
                @toggle="detail.itemRequest.deleteDialog.toggle"/>
            <Button icon="add" color="tertiary"
                :action="detail.itemRequest.itemModal.add">Add Item</Button>
            <Table :headers="['Item', 'Status', 'Quantity', '']"
                :loader="detail.isProcessing">
                <Row v-for="(r, i) in detail.data.itemRequests" :key="i">
                    <Cell label="Item">{{r.itemName}}</Cell>
                    <Cell label="Status">
                        <ButtonOptions v-if="r.statusChoices.length > 0"
                            icon="expand_more" :label="r.status"> 
                            <ButtonOption v-for="(choice, key) in r.statusChoices" :key="key"
                                @click="()=>detail.itemRequest.statusDialog.select(r.id, choice)">
                                {{choice.label}}
                            </ButtonOption>
                        </ButtonOptions>
                        <span v-else class="font-bold">
                            {{r.status}}
                        </span>
                    </Cell>
                    <Cell label="Quantity">
                        <div class="cursor-pointer hover:text-secondary"
                            @click="()=>detail.itemRequest.stockModal.select(r.id, r.status)">
                            {{r.quantityStocked}} / {{r.quantityNeededFormatted}}
                            <span class="material-icons text-sm px-2 inline-block align-middle">
                                {{['Approved', 'Partially Fulfilled'].includes(r.status) ? 
                                    'add_box' : ''}}</span>
                        </div>
                    </Cell>
                    <Cell class="px-0">
                        <div class="w-full flex justify-end">
                            <Button class="my-auto" icon="edit"
                                :disabled="['Cancelled', 'Approved', 'Partially Fulfilled', 'Fulfilled']
                                    .includes(r.status)"
                                @click="()=>detail.itemRequest.itemModal.edit(r.id)"/>
                            <Button class="my-auto" icon="delete"
                                :disabled="['Approved', 'Partially Fulfilled', 'Fulfilled']
                                    .includes(r.status)"
                                @click="()=>detail.itemRequest.deleteDialog.select(r.id)"/>
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
import ItemRequestDeleteDialog from '@/views/pages/inventory/stockrequest/ItemRequestDeleteDialog.vue';
import ItemRequestGroupModal from '@/views/pages/inventory/stockrequest/ItemRequestGroupModal.vue';

import {watch, reactive, onBeforeMount, computed} from 'vue'
import {useRoute} from 'vue-router'
import {ItemRequestGroupApi} from '@/utils/apis.js'
import {reference} from '@/utils/format.js'

export default {
    components: {
        Page, Section, Button, ButtonOptions, ButtonOption, Table, Row, Cell, 
        DescriptionItem, DescriptionList, ItemRequestAllocateStockModal, 
        ItemRequestUpdateStatusDialog, ItemRequestDeleteDialog, ItemRequestModal,
        ItemRequestGroupModal
    },
    emits: ['toggle'],
    setup() {
        const route = useRoute()
        const detail = reactive({
            id: route.params.id,
            data: {},
            itemRequestGroup: {
                editModal: {
                    data: computed(()=> {
                        let data = null;
                        if (detail.data.id) {
                            data = {
                                id: detail.data.id,
                                code: detail.data.code,
                                status: detail.data.status,
                                reason: detail.data.reason,
                                created: detail.data.created,
                            };
                        }
                        return data;
                    }),
                    isOpen: false,
                    toggle: value => detail.itemRequestGroup.editModal.isOpen = value,
                    edit: ()=> {
                        detail.itemRequestGroup.editModal.toggle(true);
                    }
                }
            },
            itemRequest: {
                stockModal: {
                    selected: null,
                    isOpen: false,
                    readOnly: true,
                    toggle: value => {
                        detail.itemRequest.stockModal.isOpen = value;
                    },
                    select: (id, status) => {
                        detail.itemRequest.stockModal.selected = id;
                        detail.itemRequest.stockModal.readOnly = 
                            !['Approved', 'Partially Fulfilled'].includes(status)
                        detail.itemRequest.stockModal.toggle(true);
                    }
                },
                itemModal: {
                    selected: null,
                    isOpen: false,
                    toggle: value => {
                        detail.itemRequest.itemModal.isOpen = value;
                    },
                    add: () => {
                        detail.itemRequest.itemModal.selected = null;
                        detail.itemRequest.itemModal.toggle(true);
                    },
                    edit: (id) => {
                        detail.itemRequest.itemModal.selected = id;
                        detail.itemRequest.itemModal.toggle(true);
                    }
                },
                statusDialog: {
                    data: {
                        id: null,
                        choice: null
                    },
                    isOpen: false,
                    toggle: value => {
                        detail.itemRequest.statusDialog.isOpen = value;
                    },
                    select: (id, choice) => {
                        detail.itemRequest.statusDialog.data = {
                            id, choice};
                        detail.itemRequest.statusDialog.toggle(true);
                    }
                },
                deleteDialog: {
                    isOpen: false,
                    itemRequestId: null,
                    data: computed(()=>{
                        let data = null;
                        const id = detail.itemRequest.deleteDialog.itemRequestId;
                        if (id) {
                            const found = detail.data.itemRequests.find(
                                i => i.id == id);
                            data = {
                                item: found.itemName,
                                quantityNeeded: found.quantityNeededFormatted
                            }
                        }
                        return data;
                    }),
                    toggle: value => detail.itemRequest.deleteDialog.isOpen = value,
                    select: id => {
                        detail.itemRequest.deleteDialog.itemRequestId = id;
                        detail.itemRequest.deleteDialog.toggle(true);
                    }
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