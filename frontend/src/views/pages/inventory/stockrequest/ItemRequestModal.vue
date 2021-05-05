<template>
     <Modal :heading="`${$props.action == 'create'?
            'Add' : 'Edit'} Item`" :is-open="$props.isOpen"
        @toggle="(value)=> $emit('toggle', value)">
        <Section>
            <div v-if="$props.action == 'create'">
                <InputTextLookup name="Item"/>
                <InputText name="Quantity" type="number"/>
            </div>
            <div v-else>
            </div>
        </Section>
    </Modal>
</template>

<script>
import Modal from '@/components/Modal.vue';
import Section from '@/components/Section.vue';
import InputText from '@/components/InputText.vue';
import InputTextLookup from '@/components/InputTextLookup.vue';

export default {
    components: {
        Modal, Section, InputText, InputTextLookup
    },
    props: {
        isOpen:Boolean,
        itemRequestId: Number,
        action: {
            type: String,
            default: 'create',
            validator: (value) => 
                ['create', 'update'].indexOf(value) !== -1
        }
    },
    emits: ['toggle']
}
</script>