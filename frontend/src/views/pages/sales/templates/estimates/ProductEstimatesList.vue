<template>
    <div>
        <Button color="secondary" icon="add"
            :action="state.createModal.open">
            Create Estimate</Button>
        <EstimateModal 
            :is-open="state.createModal.isOpen"
            :preset-data="{template: $props.templateId}"
            @toggle="state.createModal.toggle" 
            @saved="estimateId => goToDetail(estimateId)"/>
        <Table :loader="state.isProcessing"
            :headers="['Estimate', 'Quantities',  'Last Modified Date']" >
            <Row v-for="(s, key) in state.data.estimates" :key="key">
                <Cell name="Estimate">
                    <span @click="goToDetail(s.id)"
                        class="cursor-pointer underline text-secondary">
                        {{s.estimate_code}}</span>
                </Cell>
                <Cell label="Quantities">{{s.order_quantities.join(', ')}}</Cell>
                <Cell label="Last Modified Date">
                    <span>
                        {{new Date(s.updated_date).toLocaleDateString()}}
                    </span>
                </Cell>
            </Row>
        </Table>
    </div>
</template>
<script>
import Table from '@/components/Table.vue';
import Row from '@/components/Row.vue';
import Cell from '@/components/Cell.vue';
import Button from '@/components/Button.vue';
import EstimateModal from '@/views/pages/sales/estimates/EstimateModal.vue';

import {reactive, computed} from 'vue';
import {useRouter} from 'vue-router';

export default {
    components: {
        Table, Row, Cell, Button, EstimateModal
    },
    props: {
        templateId: Number,
        estimates: {
            type: Array,
            default: ()=>[]
        }
    },
    setup(props) {
        const router = useRouter();
        const state = reactive({
            isProcessing: computed(()=>props.estimates.length == 0),
            data: {
                estimates: computed(()=>props.estimates)
            },
            createModal: {
                isOpen: false,
                toggle: (value)=> state.createModal.isOpen = value,
                open: ()=> state.createModal.toggle(true)
            }
        });

        const goToDetail = (id)=> {
            router.push({ 
                name: 'sales-product-estimates-detail', 
                params: {id}});
        };

        return {
            state, goToDetail
        }
    }
}
</script>
