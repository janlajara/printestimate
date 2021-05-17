<template>
    <DeleteRecordDialog 
        heading="Delete Item Request"
        @toggle="$emit('toggle', false)"
        :is-open="$props.isOpen"
        :execute="deleteItemRequest"
        :on-after-execute="$props.onAfterExecute">
        <div>Would you like to delete this record?</div>
        <DescriptionList>
            <DescriptionItem name="Item Request" 
                :value="$props.data ? $props.data.item : null"/>
            <DescriptionItem name="Quantity Needed" 
                :value="$props.data ? $props.data.quantityNeeded : null"/>
        </DescriptionList>
    </DeleteRecordDialog> 
</template>

<script>
import DeleteRecordDialog from '@/components/DeleteRecordDialog.vue';
import DescriptionList from '@/components/DescriptionList.vue';
import DescriptionItem from '@/components/DescriptionItem.vue';

import {ItemRequestApi} from '@/utils/apis.js';

export default {
    components: {
        DeleteRecordDialog, DescriptionList, DescriptionItem
    },
    props: {
        itemRequestId: Number,
        data: Object,
        isOpen: Boolean,
        onAfterExecute: {
            type: Function,
            required: true
        }
    },
    setup(props) {
        return {
            deleteItemRequest: ()=> {
                const itemRequestId = props.itemRequestId;
                if (itemRequestId) ItemRequestApi.deleteItemRequest(itemRequestId);
            }
        }
    }
}
</script>