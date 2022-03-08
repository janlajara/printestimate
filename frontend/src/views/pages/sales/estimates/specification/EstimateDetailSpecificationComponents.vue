<template>
    <Section heading="Components">
        <Table :loader="state.isProcessing"
            :headers="['Name', 'Material/s',  'Quantity', ]" >
            <Row v-for="(s, key) in state.data.components" :key="key">
                <Cell label="Name">{{s.name}}</Cell>
                <Cell label="Material/s">
                    <ul class="pl-2 text-xs">
                        <li v-for="(x, i) in s.materials" :key="i"
                            class="list-disc">
                            {{x}}
                        </li>
                    </ul>
                </Cell>
                <Cell label="Quantity">
                    <span v-if="s.materials.length > 1">
                        {{s.quantity}} x {{s.materials.length}}
                    </span>
                    <span v-else>
                        {{s.quantity}}
                    </span>    
                </Cell>
            </Row>
        </Table>
    </Section>
</template>
<script>
import Section from '@/components/Section.vue';
import Table from '@/components/Table.vue';
import Row from '@/components/Row.vue';
import Cell from '@/components/Cell.vue';

import {reactive, computed} from 'vue';

export default {
    components: {
        Section, Table, Row, Cell
    },
    props: {
        components: {
            type: Array,
            default: ()=>[]
        }
    },
    setup(props) {
        const state = reactive({
            isProcessing: false,
            data: {
                components: computed(()=>props.components)
            },
        });

        return {
            state
        }
    }
}
</script>
