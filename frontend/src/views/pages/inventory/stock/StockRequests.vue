<template>
    <Section>
        <Table :headers="['Reason', 'Status', 'Total Quantity', 'Date Created']">
            <Row>
                <Cell label="Reason"></Cell>
                <Cell label="Status"></Cell>
                <Cell label="Total Quantity"></Cell>
                <Cell label="Date Created"></Cell>
            </Row>
        </Table>
        <TablePaginator/>
    </Section>
</template>

<script>
import Section from '@/components/Section.vue'
import Table from '@/components/Table.vue'
import Row from '@/components/Row.vue'
import Cell from '@/components/Cell.vue'
import TablePaginator from '@/components/TablePaginator.vue'

import {reactive} from 'vue'

export default {
    components: {
        Section, Table, Row, Cell, TablePaginator
    },
    props: {
        data: Object
    },
    setup() {
        const requests = reactive({
        })
        return {
            requests
        }
    }
}
</script>