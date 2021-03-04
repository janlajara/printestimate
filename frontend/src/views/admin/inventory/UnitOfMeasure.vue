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
            <Modal heading="Base Stock Unit" :is-open="bsu.modalIsOpen" @toggle="bsu.toggle"
                :buttons="[{color: 'primary', icon: 'save', text: 'Save', 
                    action: ()=>{bsu.update()}, disabled: bsu.updateIsProcessing},
                    {color: 'secondary', icon: 'save', text: 'Save and Close', 
                    action: ()=>{bsu.update(true)}, disabled: bsu.updateIsProcessing}]">
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
                        <InputSelect name="Parent Alternate Stock Unit" multiple
                            class="col-span-2" 
                            @input="bsu.input"
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
            units: [{}],
            updateIsProcessing: false,
            toggle: async (value, id=null)=> {
                bsu.selected = (id)? await retrieveBaseUnit(id) : {};
                bsu.modalIsOpen = value;
            },
            input: (value)=> {
                bsu.selected.altStockUnitIds = value;
            },
            update: async (closeModalAfter)=> {
                bsu.updateIsProcessing = true; 
                const resp = await updateBaseUnit(bsu.selected.id, bsu.selected);
                if (resp) loadTableData();
                if (closeModalAfter) bsu.modalIsOpen = false;
                bsu.updateIsProcessing = false; 
            }
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
        const loadTableData = ()=> {
            populateBaseUnits();
            populateAlternateUnits();
        }
        onBeforeMount(()=> loadTableData());

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

        const updateBaseUnit = async(id, baseStockUnit)=> {
            const request = {
                name: baseStockUnit.name,
                abbrev: baseStockUnit.abbrev,
                plural_name: baseStockUnit.pluralName,
                alternate_stock_units: Array.from(baseStockUnit.altStockUnitIds)
            };
            const response = await BaseStockUnitApi.updateBaseStockUnit(id, request);
            return response;
        }

        return {
            bsu, asu
        }
    }
}
</script>