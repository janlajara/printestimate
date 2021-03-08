<template>
    <Page title="Inventory : Stock">
        <Section>
            <Button color="secondary" :action="()=>item.toggle(true)">
                Create Item</Button>
        </Section>
        <Modal heading="Item" :is-open="item.modal.IsOpen" @toggle="item.toggle">
            <Section :heading="`${(item.modal.isCreate)? 'Create' : 'Edit'}`">
                <span v-if="item.error" class="text-sm text-red-600">*{{item.error}}</span>
                <div class="md:grid md:grid-cols-4 md:gap-4">
                    <InputText type="text" name="Name"/>
                    <InputText type="number" name="Price" postfix="PHP"/>
                </div>    
            </Section>
        </Modal>
    </Page>
</template>

<script>
import Page from '@/components/Page.vue';
import Section from '@/components/Section.vue';
import Button from '@/components/Button.vue' ;
import Modal from '@/components/Modal.vue';
import InputText from '@/components/InputText.vue';

import {reactive, computed} from 'vue';

export default {
    name: 'Stock',
    components: {
        Page, Section, Button, Modal, InputText
    },
    setup() {
        const item = reactive({
            modal: {
                isOpen: false, 
                isCreate: computed(()=> item.selected.id == null)
            },
            selected: {},
            units: [{}],
            isProcessing: false,
            error: '',
            toggle: (value, id=null)=>{
                item.error = ''; 
                if (id){
                    console.log(id);
                }
                item.modal.IsOpen = value;
            },
            validate: ()=>{},
            save: ()=>{},
            delete: ()=>{}
        });
        return {
            item
        }
    }
}
</script>