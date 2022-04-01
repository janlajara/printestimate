<template>
    <div>
        <Button color="secondary" icon="add"
            :action="state.modal.open">
            Create</Button>
        <Table :headers="['Name', 'Cost Add-ons']" :loader="state.isProcessing">
            <Row v-for="(s, key) in state.list" :key="key" clickable
                @click="()=> state.modal.open(s.id)">
                <Cell label="Name">{{s.name}}</Cell>
                <Cell label="Cost Add-ons">{{s.costAddons}}</Cell>
            </Row>
        </Table>
    </div> 
</template>
<script>
import Button from '@/components/Button.vue';
import Table from '@/components/Table.vue';
import Row from '@/components/Row.vue';
import Cell from '@/components/Cell.vue';

import {reactive} from 'vue';

export default {
    components: {
        Button, Table, Row, Cell
    },
    setup() {
        const state = reactive({
            isProcessing: false,
            list: [],
            modal: {
                isOpen: false,
                toggle: (value)=> state.modal.isOpen = value,
                open: (id=null)=> {
                    console.log(id);
                    state.modal.toggle(true);
                }
            }
        })

        return {
            state
        }
    },
}
</script>
