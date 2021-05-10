<template>
    <Dialog icon="warning_amber"
        heading="Confirm Delete"
        @toggle="$emit('toggle', false)"
        :is-open="$props.isOpen">
        <Section>
            Would you like to delete this record?
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

import {ItemRequestApi} from '@/utils/apis.js';

export default {
    components: {
        Dialog, Section, Button
    },
    props: {
        itemRequestId: Number,
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