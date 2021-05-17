<template>
    <Dialog icon="warning_amber"
        :heading="$props.heading"
        @toggle="$emit('toggle', false)"
        :is-open="$props.isOpen">
        <Section>
            <div class="grid gap-4 md:max-w-xs">
                <slot/>
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

export default {
    components: {
        Dialog, Section, Button,
    },
    props: {
        heading: String,
        isOpen: Boolean,
        execute: {
            type: Function,
            required: true,
        },
        onAfterExecute: {
            type: Function,
            required: false
        }
    },
    setup(props, {emit}) {
        const dialog = reactive({
            execute: ()=> {
                if (props.execute) {
                    props.execute()
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