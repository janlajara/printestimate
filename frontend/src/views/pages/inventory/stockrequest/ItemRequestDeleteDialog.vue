<template>
    <Dialog icon="warning_amber"
        heading="Confirm Delete"
        @toggle="$emit('toggle', false)"
        :is-open="$props.isOpen">
        <Section>
            <div class="grid gap-4">
                <div>Would you like to delete this Item Request?</div>
                <DescriptionList>
                    <DescriptionItem name="Item Request" 
                        :value="$props.data ? $props.data.item : null"/>
                    <DescriptionItem name="Quantity Needed" 
                        :value="$props.data ? $props.data.quantityNeeded : null"/>
                </DescriptionList>
            </div>
        </Section>
        <Button color="primary" class="w-full"
            @click="dialog.execute">
            Delete</Button>
    </Dialog> 
</template>

<script>
import {reactive} from 'vue';
import Dialog from '@/components/Dialog.vue';
import Section from '@/components/Section.vue';
import Button from '@/components/Button.vue';
import DescriptionList from '@/components/DescriptionList.vue';
import DescriptionItem from '@/components/DescriptionItem.vue';

import {ItemRequestApi} from '@/utils/apis.js';

export default {
    components: {
        Dialog, Section, Button, DescriptionList, DescriptionItem
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
    setup(props, {emit}) {
        const dialog = reactive({
            execute: ()=> {
                const itemRequestId = props.itemRequestId;
                if (itemRequestId) {
                    ItemRequestApi.deleteItemRequest(itemRequestId);
                    if (props.onAfterExecute) props.onAfterExecute();
                    emit('toggle', false)
                }
            }
        })
        return {
            dialog
        }
    }
}
</script>