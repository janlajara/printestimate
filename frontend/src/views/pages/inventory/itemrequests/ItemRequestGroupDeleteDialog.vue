<template>
    <DeleteRecordDialog 
        :heading="`Delete ${$props.data ? $props.data.code: ''}`"
        @toggle="$emit('toggle', false)"
        :is-open="$props.isOpen"
        :execute="deleteItemRequestGroup"
        :on-after-execute="$props.onAfterExecute">
        <div>Deleting 
            <span class="font-bold">
                {{$props.data ? $props.data.code : ''}}</span>
                would also delete all the associated item requests.</div>
        <div>Would you like to proceed?</div>
    </DeleteRecordDialog> 
</template>

<script>
import DeleteRecordDialog from '@/components/DeleteRecordDialog.vue';
import {ItemRequestGroupApi} from '@/utils/apis.js';

export default {
    components: {
        DeleteRecordDialog
    },
    props: {
        itemRequestGroupId: Number,
        data: Object,
        isOpen: Boolean,
        onAfterExecute: {
            type: Function,
            required: true
        }
    },
    setup(props) {
        return {
            deleteItemRequestGroup: ()=> {
                const itemRequestGroupId = props.itemRequestGroupId;
                if (itemRequestGroupId) 
                    ItemRequestGroupApi.deleteItemRequestGroup(itemRequestGroupId);
            }
        }
    }
}
</script>