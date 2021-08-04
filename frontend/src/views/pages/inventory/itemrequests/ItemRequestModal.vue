<template>
     <Modal :heading="`${item.isCreate ?
            'Add' : 'Edit'} Item Request`" :is-open="$props.isOpen"
        @toggle="(value)=> $emit('toggle', value)"
        :buttons="[{color: 'primary', icon:'save', text:'Save', 
                    action: item.isCreate ? item.add : item.update, 
                    disabled: item.form.disabled},]">
        <Section heading="General Information" heading-position="side"> 
            <div class="md:grid md:gap-4 md:grid-cols-3">
                <InputTextLookup v-if="item.isCreate"
                    name="Item" class="md:col-span-2"
                    placeholder="Search Item"
                    :value="item.form.input"
                    @select="item.form.select"
                    @input="item.search"
                    :options="item.list.map( option => ({
                        value: option.id,
                        title: option.name,
                        subtitle: option.type,
                        figure: option.availableFormatted,
                        timestamp: null
                    }))"/>
                <InputText v-else class="md:col-span-2"
                    name="Item Name" disabled 
                    type="text" :value="item.form.input"/>
                <InputText name="Quantity Needed"  placeholder="Quantity"
                    type="number" :postfix="item.form.selected.uom"
                    :value="item.form.quantity"
                    @input="value => item.form.quantity = value"/>
            </div>
        </Section>
    </Modal>
</template>

<script>
import Modal from '@/components/Modal.vue';
import Section from '@/components/Section.vue';
import InputText from '@/components/InputText.vue';
import InputTextLookup from '@/components/InputTextLookup.vue';

import {reactive, computed, watch} from 'vue';
import {ItemApi, ItemRequestApi, ItemRequestGroupApi} from '@/utils/apis.js';

export default {
    components: {
        Modal, Section, InputText, InputTextLookup
    },
    props: {
        isOpen:Boolean,
        itemRequestGroupId: Number,
        itemRequestId: Number,
        onAfterAdd: Function
    },
    emits: ['toggle'],
    setup(props, {emit}) {
        const item = reactive({
            isCreate: computed(()=> props.itemRequestId == null),
            isProcessing: false,
            list: [],
            form: {
                selected: {
                    id: null,
                    uom: '  '
                },
                input: '',
                quantity: 0,
                disabled: computed(()=> 
                    !(item.form.selected.id && item.form.quantity > 0) || item.isProcessing),
                select: id => {
                    if (id) { 
                        item.form.selected.id = id;
                        const found = item.list.find(i => i.id == id);
                        if (found)
                            item.form.selected.uom = found.baseUom; 
                    }
                },
                clear: () => {
                    item.form.selected = {id: null, uom: '  '};
                    item.form.input = '';
                    item.form.quantity = 0;
                }
            },
            search: value => {
                item.form.input = value;
                lookupItems(value);
            },
            add: () => {
                const itemId = item.form.selected.id;
                const quantity = item.form.quantity;
                addItemRequest(props.itemRequestGroupId, itemId, quantity);
            },
            update: () => {
                const itemRequestId = props.itemRequestId;
                updateItemRequest(itemRequestId, item.form.quantity);
            },
            retrieve: async (itemRequestId) => {
                const itemRequest = await retrieveItemRequest(itemRequestId);
                if (itemRequest) {
                    item.form.input = itemRequest.item_name;
                    item.form.quantity = itemRequest.quantity_needed;
                    item.form.selected.id = itemRequestId;
                    item.form.selected.uom = itemRequest.item_base_uom.abbrev;
                }
            }
        });

        const lookupItems = async(search) => {
            item.isProcessing = true;
            const response = await ItemApi.listItems(10, 0, search);
            if (response && response.results) {
                item.list = response.results.map(i=> ({
                    id: i.id, name: i.full_name, type: i.type,
                    baseUom: i.base_uom, 
                    available: i.available_quantity,
                    availableFormatted: i.available_quantity_formatted,
                    onhand: i.onhand_quantity,
                    onhandFormatted: i.onhand_quantity_formatted,
                    price: i.price
                }))
            }
            item.isProcessing = false;
        }

        const retrieveItemRequest = async(itemRequestId) => {
            item.isProcessing = true;
            if (itemRequestId) {
                const response = await ItemRequestApi.retrieveItemRequest(itemRequestId);
                if (response) {
                    item.isProcessing = false;
                    return response;
                }
            }
            item.isProcessing = false;
        }

        const updateItemRequest = async(itemRequestId, quantity) => {
            item.isProcessing = true;
            if (itemRequestId) {
                const request = {
                    quantity_needed: quantity};
                const response = await ItemRequestApi.updateItemRequest(itemRequestId, request);
                if (response) {
                    if (props.onAfterAdd) props.onAfterAdd();
                    emit('toggle', false);
                }
            }
            item.isProcessing = false;
        }

        const addItemRequest = async(itemRequestGroupId, itemId, quantity) => {
            item.isProcessing = true;
            if (itemRequestGroupId && itemId && quantity > 0) {
                const request = {
                    item_id: itemId,
                    quantity: quantity}
                const response = await ItemRequestGroupApi.addItemRequest(
                    itemRequestGroupId, request)
                if (response) {
                    if (props.onAfterAdd) props.onAfterAdd();
                    emit('toggle', false);
                }
            }
            item.isProcessing = false;
        }

        watch(()=> props.isOpen, ()=> {
            const itemRequestId = props.itemRequestId;
            if (props.isOpen) { 
                if (itemRequestId == null) item.form.clear();
                else if (itemRequestId) {
                    item.retrieve(itemRequestId);
                }
            }
        })

        return {
            item, lookupItems
        }
    }
}
</script>