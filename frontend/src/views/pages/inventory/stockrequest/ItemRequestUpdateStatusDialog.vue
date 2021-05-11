<template>
    <Dialog icon="contact_support"
        :heading="`Confirm ${dialog.choice.label}`"
        @toggle="$emit('toggle', false)"
        :is-open="$props.isOpen">
        <Section>
            <div class="grid gap-4">
                <div>Would you like to update the status of this request?</div>
                <InputTextarea name="Comments"
                    @input="value => dialog.comments = value"/>
            </div>
        </Section>
        <Button color="primary" class="w-full"
            @click="dialog.execute">
            Confirm</Button>
    </Dialog> 
</template>

<script>
import {reactive, watch} from 'vue';
import Dialog from '@/components/Dialog.vue';
import Section from '@/components/Section.vue';
import InputTextarea from '@/components/InputTextarea.vue';
import Button from '@/components/Button.vue';

import {ItemRequestApi} from '@/utils/apis.js';

export default {
    components: {
        Dialog, Section, InputTextarea, Button
    },
    props: {
        data: Object,
        isOpen:Boolean,
        onAfterExecute: Function
    },
    emits: ['toggle'],
    setup(props, {emit}) {
        const dialog = reactive({
            id: null,
            choice: {
                label: null,
                value: null
            },
            comments: null,
            execute: async ()=> {
                if (dialog.id && dialog.choice.value) {
                    const request = {
                        status: dialog.choice.value,
                        comments: dialog.comments
                    };
                    const response = await ItemRequestApi.updateItemRequestStatus(dialog.id, request);
                    if (response) {
                        emit('toggle', false);
                        if (props.onAfterExecute) props.onAfterExecute();
                    }
                }
            }
        });
        watch(()=> props.data, ()=> {
            if (props.data && props.data.id) {
                dialog.id = props.data.id;
                if (props.data.choice) {
                    dialog.choice = {
                        label: props.data.choice.label,
                        value: props.data.choice.value
                    }
                }
            } else {
                dialog.id = null;
                dialog.choice = {
                    label: null, value: null
                }
            }
        })
        return {
            dialog
        }
    }
}
</script>