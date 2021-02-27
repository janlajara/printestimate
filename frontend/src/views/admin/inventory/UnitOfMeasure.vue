<template>
    <div>
        <Section heading="Base Stock Unit" 
            description="Individual units of measure.">
            <Table :headers="['Unit name', 'Abbreviation', 'Plural', 
                'Abbreviation (Pl.)', 'Parent Alternate Stock Units']">
                <Row v-for="(unit, key) in bsu.units" :key="key"
                    :select="()=>{bsu.toggle(true, unit.id)}">
                    <Cell label="Name">{{unit.name}}</Cell>
                    <Cell label="Abbrev.">{{unit.abbrev}}</Cell>
                    <Cell label="Plural Name">{{unit.pluralName}}</Cell>
                    <Cell label="Plural Abbrev.">{{unit.pluralAbbrev}}</Cell>
                    <Cell label="Parent Alternate Stock Units">
                        {{unit.altStockUnits}}
                    </Cell>
                </Row>
            </Table>
            <Modal heading="Base Stock Unit" :is-open="bsu.modalIsOpen" @toggle="bsu.toggle">
                <Section :heading="bsu.selected.name">
                    <div class="md:grid md:grid-cols-4 md:gap-4">
                        <InputText name="Name" type="text" :value="bsu.selected.name"
                            @input="(e)=>bsu.selected.name = e.target.value"/>
                        <InputText name="Abbreviation" type="text" :value="bsu.selected.abbrev"
                            @input="(e)=>bsu.selected.abbrev = e.target.value"/>
                        <InputText name="Name (Plural)" type="text" :value="bsu.selected.pluralName"
                            @input="(e)=>bsu.selected.pluralName = e.target.value" disabled/>
                        <InputText name="Abbreviation (Plural)" type="text" :value="bsu.selected.pluralAbbrev"
                            @input="(e)=>bsu.selected.pluralAbbrev = e.target.value" disabled/>
                        <InputSelect name="Parent Alternate Stock Unit" 
                            class="col-span-2" 
                            @input="(value)=>bsu.selected.altStockUnitIds = value"
                            :options="asu.units.map(unit=> ({
                                label: unit.name, value: unit.id, 
                                isSelected: bsu.selected.altStockUnitIds.indexOf(unit.id) != -1
                            }))"/>
                    </div>
                </Section>
            </Modal>
        </Section>
        <hr class="my-6"/>
        <Section heading="Alternate Stock Unit" 
            description="Grouped units of measure.">
            <Table :headers="['Unit name', 'Abbreviation', 'Plural', 
                'Abbreviation (Pl.)', 'Child Base Stock Units']">
                <Row v-for="(unit, key) in asu.units" :key="key">
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
import Modal from '@/components/Modal.vue'
import InputText from '@/components/InputText.vue'
import InputSelect from '@/components/InputSelect.vue'

import {reactive, onBeforeMount} from 'vue';
import {BaseStockUnitApi, AlternateStockUnitApi} from '@/utils/apis.js';

export default {
    name: "UnitOfMeasure",
    components: {
        Section, Table, Row, Cell, Modal, InputText, InputSelect
    },
    setup() {
        const bsu = reactive({
            modalIsOpen: false,
            selected: {},
            toggle: async (value, id=null)=> {
                if (id) {
                    bsu.selected = await retrieveBaseUnit(id);
                } else {
                    bsu.selected = {};
                }
                bsu.modalIsOpen = value;
            },
            units: [{}]
        })
        const asu = reactive({
            modalIsOpen: false,
            toggle: (value)=> asu.modalIsOpen = value,
            units: [{}]
        })
        const populateBaseUnits = async ()=> {
            const data = await BaseStockUnitApi.listBaseStockUnits();
            bsu.units = data.map( baseUnit => ({
                id: baseUnit.id,
                name: baseUnit.name, 
                abbrev: baseUnit.abbrev, 
                pluralName: baseUnit.plural_name, 
                pluralAbbrev: baseUnit.plural_abbrev, 
                altStockUnits: baseUnit.alternate_stock_units.join(', ')
            }));
        }
        const populateAlternateUnits = async ()=> {
            const data = await AlternateStockUnitApi.listAlternateStockUnits();
            asu.units = data.map( alternateUnit => ({
                id: alternateUnit.id,
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

        const retrieveBaseUnit = async (id)=> {
            const data = await BaseStockUnitApi.retrieveBaseStockUnit(id);
            const baseUnit = {
                id: data.id,
                name: data.name,
                abbrev: data.abbrev,
                pluralName: data.plural_name,
                pluralAbbrev: data.plural_abbrev,
                isEditable: data.is_editable,
                altStockUnitIds: data.alternate_stock_units
                    .map(unit=> unit.id)
            };
            return baseUnit;
        }

        return {
            bsu, asu 
        }
    }
}
</script>