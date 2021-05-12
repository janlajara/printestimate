<template>
    <Modal :heading="modal.isCreate? 'Create MRS' : `Edit ${$props.data.code}`" 
        :is-open="$props.isOpen"
        :buttons="[{color: 'primary', icon:'save', text:'Save', 
                    action: modal.isCreate ? modal.add : modal.update, 
                    disabled: modal.isProcessing}]"
        @toggle="$emit('toggle', value)">
        <Section heading="General Information" heading-position="side"> 
            <div v-if="modal.isCreate" class="md:grid md:gap-4 md:grid-cols-3">

            </div>
            <div v-else class="md:grid md:gap-4">
                <DescriptionList class="md:grid md:grid-cols-2">
                    <DescriptionItem name="Status" 
                        :value="modal.form.status"/>
                    <DescriptionItem name="Date Created" 
                        :value="modal.form.created"/>
                </DescriptionList>
                <hr/>
                <InputTextarea name="Reason" 
                    :value="modal.form.reason"
                    @input="value => modal.form.reason=value"/>            
            </div>
        </Section>
    </Modal>
</template>

<script>
import Modal from '@/components/Modal.vue';
import Section from '@/components/Section.vue';
import InputTextarea from '@/components/InputTextarea.vue';
import DescriptionItem from '@/components/DescriptionItem.vue';
import DescriptionList from '@/components/DescriptionList.vue';

import {reactive, computed, watch} from 'vue';
import {ItemRequestGroupApi} from '@/utils/apis.js';

export default {
    components: {
        Modal, Section, InputTextarea, DescriptionItem, DescriptionList
    },
    props: {
        isOpen: Boolean,
        data: Object,
        onAfterSave: Function
    },
    emits: ['toggle'],
    setup(props, {emit}) {
        const modal = reactive({
            isCreate: computed(()=> props.data == null),
            isProcessing: false,
            form: {
                id: null,
                status: null,
                reason: null,
                created: null
            },
            add: ()=> {

            },
            update: async ()=> {
                const response = await updateItemRequestGroup();
                if (response) emit('toggle', false);
            }
        });

        const updateItemRequestGroup = async ()=> {
            modal.isProcessing = true;
            const request = {
                reason: modal.form.reason};
            const response = await ItemRequestGroupApi.updateItemRequestGroup(
                modal.form.id, request);
            if (response) {
                if (props.onAfterSave) props.onAfterSave();
                modal.isProcessing = false;
                return response;
            }
            modal.isProcessing = false;
        }

        watch(()=> props.isOpen, ()=> {
            if (props.data) {
                const data = props.data;
                modal.form = {
                    id: data.id,
                    status: data.status,
                    reason: data.reason,
                    created: data.created
                }
            }
        })

        return {
            modal
        }
    }
}
</script>