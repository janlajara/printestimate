<template>
    <Dialog icon="warning_amber"
        heading="Confirm Delete"
        @toggle="$emit('toggle', false)"
        :is-open="$props.isOpen">
        <Section>
            <div class="grid gap-4 md:max-w-xs">
                <div>Deleting 
                    <span class="font-bold">
                        {{$props.data ? $props.data.code : ''}}</span>
                     would also delete all the associated item requests.</div>
                <div>Would you like to proceed?</div>
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

import {ItemRequestGroupApi} from '@/utils/apis.js';

export default {
    components: {
        Dialog, Section, Button,
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
    setup(props, {emit}) {
        const dialog = reactive({
            execute: ()=> {
                const itemRequestGroupId = props.itemRequestGroupId;
                if (itemRequestGroupId) {
                    ItemRequestGroupApi.deleteItemRequestGroup(itemRequestGroupId);
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