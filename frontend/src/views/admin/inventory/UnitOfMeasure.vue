<template>
    <div>
        <Section heading="Base Stock Unit" 
            description="Individual units of measure.">
            <Table :headers="['Unit name', 'Abbreviation', 'Plural', 
                'Abbreviation (Pl.)', 'Parent Alternate Stock Units']">
                    <Row v-for="(unit, key) in baseUnits" :key="key">
                    <Cell>{{unit.name}}</Cell>
                    <Cell>{{unit.abbrev}}</Cell>
                    <Cell>{{unit.pluralName}}</Cell>
                    <Cell>{{unit.pluralAbbrev}}</Cell>
                    <Cell>{{unit.altStockUnits}}</Cell>
                </Row>
            </Table>
        </Section>
        <hr class="my-6"/>
        <Section heading="Alternate Stock Unit" 
            description="Grouped units of measure.">
            <Table :headers="['Unit name', 'Abbreviation', 'Plural', 
                'Abbreviation (Pl.)', 'Child Base Stock Units']">
                <Row v-for="(unit, key) in alternateUnits" :key="key">
                    <Cell>{{unit.name}}</Cell>
                    <Cell>{{unit.abbrev}}</Cell>
                    <Cell>{{unit.pluralName}}</Cell>
                    <Cell>{{unit.pluralAbbrev}}</Cell>
                    <Cell>{{unit.baseStockUnits}}</Cell>
                </Row>
            </Table>
        </Section>
    </div>
</template>
<script>
import Section from '@/components/Section.vue'
import Table from '@/components/Table.vue'
import Row from '@/components/Row.vue'
import Cell from '@/components/Cell.vue'

import {reactive, toRefs, onBeforeMount} from 'vue';
import {BaseStockUnitApi, AlternateStockUnitApi} from '@/utils/apis.js';

export default {
    name: "UnitOfMeasure",
    components: {
        Section, Table, Row, Cell
    },
    setup() {
        const units = reactive({
            baseUnits: [{}],
            alternateUnits: [{}]
        })
        const populateBaseUnits = async ()=> {
            const data = await BaseStockUnitApi.listBaseStockUnits();
            units.baseUnits = data.map( baseUnit => ({
                name: baseUnit.name, 
                abbrev: baseUnit.abbrev, 
                pluralName: baseUnit.plural_name, 
                pluralAbbrev: baseUnit.plural_abbrev, 
                altStockUnits: baseUnit.alternate_stock_units.join(', ')
            }));
        }
        const populateAlternateUnits = async ()=> {
            const data = await AlternateStockUnitApi.listAlternateStockUnits();
            units.alternateUnits = data.map( alternateUnit => ({
                name: alternateUnit.name, 
                abbrev: alternateUnit.abbrev,
                pluralName: alternateUnit.plural_name, 
                pluralAbbrev: alternateUnit.plural_abbrev, 
                baseStockUnits: alternateUnit.base_stock_units.join(', ')
            }));
        }

        onBeforeMount(()=> {
            populateBaseUnits();
            populateAlternateUnits();
        })
        
        return {
            ...toRefs(units)
        }
    }
}
</script>