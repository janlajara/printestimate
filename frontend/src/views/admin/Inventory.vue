<template>
    <Page title="Admin : Inventory">
        <Tabs>
            <Tab title="Item">
                <Section heading="General Content" description="General tab content goes here.">
                    
                </Section>
            </Tab>
            <Tab title="Unit of Measure">
                <Section heading="Base Stock Unit" 
                    description="Individual units of measure.">
                    <Table :headers="['Unit name', 'Abbreviation', 'Plural', 
                        'Abbreviation (Pl.)', 'Parent Alternate Stock Units']"
                        :rows="baseUnits"/>
                </Section>
                <hr class="my-6"/>
                <Section heading="Alternate Stock Unit" 
                    description="Grouped units of measure.">
                    <Table :headers="['Unit name', 'Abbreviation', 'Plural', 
                        'Abbreviation (Pl.)', 'Child Base Stock Units']"
                        :rows="alternateUnits"/>
                </Section>
            </Tab>
        </Tabs>
    </Page>
</template>

<script>
import Page from '@/components/Page.vue';
import Tabs from '@/components/Tabs.vue';
import Tab from '@/components/Tab.vue';
import Section from '@/components/Section.vue';
import Table from '@/components/Table.vue';

import {ref} from 'vue';
import {BaseStockUnitApi, AlternateStockUnitApi} from '@/utils/apis.js';

export default {
    components: {
        Page, Tabs, Tab, Section, Table
    },
    setup()  {
        const baseUnits = ref([]);
        const alternateUnits = ref([]);
        const populateBaseUnits = async ()=> {
            const units = await BaseStockUnitApi.listBaseStockUnits();
            baseUnits.value = units.map( baseUnit => (
                [baseUnit.name, baseUnit.abbrev, 
                baseUnit.plural_name, baseUnit.plural_abbrev, 
                baseUnit.alternate_stock_units.join(', ')]
            ));
        }
        const populateAlternateUnits = async ()=> {
            const units = await AlternateStockUnitApi.listAlternateStockUnits();
            alternateUnits.value = units.map( alternateUnit => (
                [alternateUnit.name, alternateUnit.abbrev,
                alternateUnit.plural_name, alternateUnit.plural_abbrev, 
                alternateUnit.base_stock_units.join(', ')]
            ));
        }

        populateBaseUnits();
        populateAlternateUnits();

        return {
            baseUnits, alternateUnits
        }
    }
}
</script>