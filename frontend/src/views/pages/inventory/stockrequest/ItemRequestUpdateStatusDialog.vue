<template>
    <Dialog
        heading="Would you like to proceed with this action?"
        @toggle="$emit('toggle', false)"
        :is-open="$props.isOpen">
        <Section>
            <InputTextarea name="Comments"
                @input="value => dialog.comments = value"/>
        </Section>
        <Button color="primary" class="w-full"
            @click="dialog.execute">
            Confirm {{dialog.choice.label}}</Button>
    </Dialog> 
</template>

<script>
import {reactive, onUpdated} from 'vue';
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
                    const response = await ItemRequestApi.updateItemRequest(dialog.id, request);
                    if (response) {
                        emit('toggle', false);
                        if (props.onAfterExecute) props.onAfterExecute();
                    }
                }
            }
        });
        onUpdated(()=> {
            if (props.data) {
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