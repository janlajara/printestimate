<template>
    <div>
        <DeleteRecordDialog 
            :heading="`Delete ${deleteDialog.data.name}`"
            :is-open="deleteDialog.isOpen"
            @toggle="deleteDialog.toggle"
            :execute="deleteDialog.data.executeFunc">
            <div>
                Are you sure you want to delete 
                <span class="font-bold">
                    {{deleteDialog.data.name}}</span>?
            </div>
        </DeleteRecordDialog>
        <Section heading="Base Stock Unit" 
            description="Individual units of measure.">
            <Button color="secondary" :action="()=>bsu.toggle(true)">Create</Button>
            <Table :headers="['Name', 'Abbreviation',  
                'Parent Alternate Stock Units', '']">
                <Row v-for="(unit, key) in bsu.units" :key="key"
                    :class="unit.isEditable? []: 'row-disabled'">
                    <Cell label="Name">{{unit.name}} ({{unit.pluralName}})</Cell>
                    <Cell label="Abbrev.">{{unit.abbrev}} ({{unit.pluralAbbrev}})</Cell>
                    <Cell label="Parent Alternate Stock Units">
                        {{unit.altStockUnits}}
                    </Cell>
                    <Cell class="flex-grow">
                        <div class="flex justify-end">
                            <Button class="my-auto" icon="edit"
                                :disabled="!unit.isEditable"
                                @click="()=>bsu.toggle(true, unit.id)"/>
                            <Button class="my-auto" icon="delete"
                                :disabled="!unit.isEditable"
                                @click="deleteDialog.open(
                                    unit.name, ()=>bsu.delete(unit.id))"/>
                        </div>
                    </Cell>
                </Row>
            </Table>
            <Modal :heading="bsu.modal.isCreate ? 'Create Base Stock Unit' : 
                    'Edit ' + bsu.selected.name"
                :is-open="bsu.modal.IsOpen" @toggle="bsu.toggle"
                :buttons="[
                    {color: 'primary', icon: 'save', text: 'Save', 
                        action: ()=>{bsu.save()}, disabled: bsu.isProcessing},
                    {color: 'secondary', icon: 'save', text: 'Save and Close', 
                        action: ()=>{bsu.save(true)}, disabled: bsu.isProcessing}]">
                <div v-if="bsu.error" class="text-sm pt-4 text-red-600">*{{bsu.error}}</div>
                <Section heading="General Information" heading-position="side">
                    <div class="md:grid md:grid-cols-3 md:gap-4">
                        <InputText name="Name" type="text" :value="bsu.selected.name" required
                            @input="(value)=>bsu.selected.name = value"/>
                        <InputText name="Abbreviation" type="text" :value="bsu.selected.abbrev" required
                            @input="(value)=>bsu.selected.abbrev = value"/>
                        <InputText name="Name (Plural)" type="text" :value="bsu.selected.pluralName"
                            @input="(value)=>bsu.selected.pluralName = value" disabled/>
                        <InputText name="Abbreviation (Plural)" type="text" :value="bsu.selected.pluralAbbrev"
                            @input="(value)=>bsu.selected.pluralAbbrev = value" disabled/>
                        <InputSelect name="Parent Alternate Stock Unit" multiple
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
        <hr/>
        <Section heading="Alternate Stock Unit" 
            description="Grouped units of measure.">
            <Button color="secondary" :action="()=>asu.toggle(true)">Create</Button>
            <Table :headers="['Name', 'Abbreviation', 'Child Base Stock Units', '']">
                <Row v-for="(unit, key) in asu.units" :key="key"
                    :class="unit.isEditable? []: 'row-disabled'">
                    <Cell label="Name">{{unit.name}} ({{unit.pluralName}})</Cell>
                    <Cell label="Abbrev.">{{unit.abbrev}} ({{unit.pluralAbbrev}})</Cell>
                    <Cell label="Parent Alternate Stock Units">{{unit.baseStockUnits}}</Cell>
                    <Cell class="flex-grow">
                        <div class="flex justify-end">
                            <Button class="my-auto" icon="edit"
                                :disabled="!unit.isEditable"
                                @click="()=>asu.toggle(true, unit.id)"/>
                           <Button class="my-auto" icon="delete"
                                :disabled="!unit.isEditable"
                                @click="deleteDialog.open(
                                    unit.name, ()=>asu.delete(unit.id))"/>
                        </div>
                    </Cell>
                </Row>
            </Table>
            <Modal :heading="`${(asu.modal.isCreate)?  'Create Alternate Stock Unit' : 'Edit ' + asu.selected.name}`" 
                :is-open="asu.modal.IsOpen" @toggle="asu.toggle"
                :buttons="[{color: 'primary', icon: 'save', text: 'Save', 
                    action: ()=>{asu.save()}, disabled: asu.isProcessing},
                    {color: 'secondary', icon: 'save', text: 'Save and Close', 
                    action: ()=>{asu.save(true)}, disabled: asu.isProcessing}]">
                <div v-if="asu.error" class="text-sm pt-4 text-red-600">*{{asu.error}}</div>
                <Section heading="General Information" heading-position="side">
                    <div class="md:grid md:grid-cols-3 md:gap-4">
                        <InputText name="Name" type="text" :value="asu.selected.name"
                            @input="(value)=>asu.selected.name = value"/>
                        <InputText name="Abbreviation" type="text" :value="asu.selected.abbrev"
                            @input="(value)=>asu.selected.abbrev = value"/>
                        <InputText name="Name (Plural)" type="text" :value="asu.selected.pluralName"
                            @input="(value)=>asu.selected.pluralName = value" disabled/>
                        <InputText name="Abbreviation (Plural)" type="text" :value="asu.selected.pluralAbbrev"
                            @input="(value)=>asu.selected.pluralAbbrev = value" disabled/>
                        <InputSelect name="Parent Alternate Stock Unit" multiple
                            class="col-span-2" 
                            @input="(value)=>asu.selected.baseStockUnitIds = value"
                            :options="bsu.units.map(unit=> ({
                                label: unit.name, value: unit.id, 
                                isSelected: asu.selected.baseStockUnitIds.indexOf(unit.id) != -1
                            }))"/>
                    </div>
                </Section>
            </Modal>
        </Section>
    </div>
</template>
<script>
import Section from '@/components/Section.vue'
import Button from '@/components/Button.vue'
import Table from '@/components/Table.vue'
import Row from '@/components/Row.vue'
import Cell from '@/components/Cell.vue'
import Modal from '@/components/Modal.vue'
import InputText from '@/components/InputText.vue'
import InputSelect from '@/components/InputSelect.vue'
import DeleteRecordDialog from '@/components/DeleteRecordDialog.vue';

import {reactive, onBeforeMount} from 'vue';
import {BaseStockUnitApi, AlternateStockUnitApi} from '@/utils/apis.js';

export default {
    name: "UnitOfMeasure",
    components: {
        Section, Button, Table, Row, Cell, Modal, 
        InputText, InputSelect, DeleteRecordDialog
    },
    setup() {
        const deleteDialog = reactive({
            isOpen: false,
            data: {
                name: '', 
                executeFunc: ()=>{}},
            toggle: value => deleteDialog.isOpen = value,
            open: (name, executeFunc) => {
                deleteDialog.data={name, executeFunc};
                deleteDialog.toggle(true);
            }
        });
        const bsu = reactive({
            modal: {
                isOpen: false,
                isCreate: false
            },
            selected: {
                id: null, name: '', 
                abbrev: '', pluralName: null, 
                pluralAbbrev: null, altStockUnitIds: []},
            units: [{}],
            isProcessing: false,
            error: '',
            toggle: async (value, id=null)=> {
                bsu.error = '';
                if (id != null) {
                    bsu.selected = (id)? await retrieveBaseUnit(id) : {};
                    bsu.modal.isCreate = false;
                } else {
                    bsu.selected = {id: null, name: '', abbrev: '', pluralName: null, 
                        pluralAbbrev: null, altStockUnitIds: []};
                    bsu.modal.isCreate = true;
                }
                bsu.modal.IsOpen = value;
            },
            validate: ()=> {
                let errors = []
                if (bsu.selected.name.length == 0) errors.push('name');
                if (bsu.selected.abbrev.length == 0) errors.push('abbrev');
                if (errors.length > 0)
                    bsu.error = `The following fields must not be empty: ${errors.join(', ')}.`;
                return errors.length > 0;
            },
            save: async (closeModalAfter)=> {
                if (bsu.validate()) return;

                bsu.isProcessing = true; 
                let data;
                if (bsu.selected.id) data = await updateBaseUnit(bsu.selected.id, bsu.selected);
                else data = await createBaseUnit(bsu.selected);

                if (data) {
                    loadTableData(); 
                    bsu.selected = await retrieveBaseUnit(data.id);
                    bsu.modal.isCreate = false;
                }
                if (closeModalAfter) bsu.modal.IsOpen = false;
                bsu.isProcessing = false; 
            },
            delete: async (id)=> {
                bsu.isProcessing = true; 
                await deleteBaseUnit(id);
                loadTableData();
                bsu.isProcessing = false;
            },
        })
        const asu = reactive({
            modal: {
                isOpen: false,
                isCreate: false
            },
            selected: {id: null, name: '', 
                abbrev: '', pluralName: null, 
                pluralAbbrev: null, baseStockUnitIds: []},
            units: [{}],
            isProcessing: false,
            error: '',
            toggle: async (value, id=null)=> {
                asu.error = '';
                if (id != null) {
                    asu.selected = (id)? await retrieveAlternateUnit(id) : {};
                    asu.modal.IsOpen = value;
                    asu.modal.isCreate = false;
                } else {
                    asu.selected = {id: null, name: '', abbrev: '', pluralName: null, 
                        pluralAbbrev: null, baseStockUnitIds: []};
                    asu.modal.isCreate = true;
                }
                asu.modal.IsOpen = value;
            },
            validate: ()=> {
                let errors = []
                if (asu.selected.name.length == 0) errors.push('name');
                if (asu.selected.abbrev.length == 0) errors.push('abbrev');
                if (errors.length > 0)
                    asu.error = `The following fields must not be empty: ${errors.join(', ')}.`;
                return errors.length > 0;
            },
            save: async (closeModalAfter)=> {
                if (asu.validate()) return;

                asu.isProcessing = true; 
                let data;
                if (asu.selected.id) data = await updateAlternateUnit(asu.selected.id, asu.selected);
                else data = await createAlternateUnit(asu.selected);

                if (data) {
                    loadTableData(); 
                    asu.selected = await retrieveAlternateUnit(data.id);
                    asu.modal.isCreate = false;
                }
                if (closeModalAfter) asu.modal.IsOpen = false;
                asu.isProcessing = false; 
            },
            delete: async (id)=> {
                asu.isProcessing = true; 
                await deleteAlternateUnit(id);
                loadTableData();
                asu.isProcessing = false;
            },
        })
        const populateBaseUnits = async ()=> {
            const data = await BaseStockUnitApi.listBaseStockUnits();
            bsu.units = data.map( baseUnit => ({
                id: baseUnit.id,
                name: baseUnit.name, 
                abbrev: baseUnit.abbrev, 
                isEditable: baseUnit.is_editable,
                pluralName: baseUnit.plural_name, 
                pluralAbbrev: baseUnit.plural_abbrev, 
                altStockUnits: baseUnit.alternate_stock_units
                    .map(unit => unit.name)
                    .join(', ')
            }));
        }
        const populateAlternateUnits = async ()=> { 
            const data = await AlternateStockUnitApi.listAlternateStockUnits();
            asu.units = data.map( alternateUnit => ({
                id: alternateUnit.id,
                name: alternateUnit.name, 
                abbrev: alternateUnit.abbrev,
                isEditable: alternateUnit.is_editable,
                pluralName: alternateUnit.plural_name, 
                pluralAbbrev: alternateUnit.plural_abbrev, 
                baseStockUnits: alternateUnit.base_stock_units
                    .map(unit => unit.name)
                    .join(', ')
            }));
        }
        const loadTableData = ()=> {
            populateBaseUnits();
            populateAlternateUnits();
        }
        onBeforeMount(()=> loadTableData());

        // BASE UNIT FUNCTIONS
        const serializeBaseUnit = (baseStockUnit)=> {
            if (baseStockUnit) {
                return {
                    name: baseStockUnit.name,
                    abbrev: baseStockUnit.abbrev,
                    plural_name: baseStockUnit.pluralName,
                    alternate_stock_units: Array.from(baseStockUnit.altStockUnitIds)
                };
            }
        }
        const deserializeBaseUnit = (json)=> {
            if (json) {
                return {
                    id: json.id, name: json.name,
                    abbrev: json.abbrev, pluralName: json.plural_name,
                    pluralAbbrev: json.plural_abbrev,
                    isEditable: json.is_editable,
                    altStockUnitIds: json.alternate_stock_units
                        .map(unit=> unit.id)
                };
            }
        }
        const retrieveBaseUnit = async (id)=> {
            const response = await BaseStockUnitApi.retrieveBaseStockUnit(id);
            return deserializeBaseUnit(response);
        }
        const createBaseUnit = async(baseStockUnit)=> {
            const request = serializeBaseUnit(baseStockUnit);
            const response = await BaseStockUnitApi.createBaseStockUnit(request);
            return deserializeBaseUnit(response);
        }
        const updateBaseUnit = async(id, baseStockUnit)=> {
            const request = serializeBaseUnit(baseStockUnit);
            const response = await BaseStockUnitApi.updateBaseStockUnit(id, request);
            return deserializeBaseUnit(response);
        }
        const deleteBaseUnit = async(id)=> {
            const response = await BaseStockUnitApi.deleteBaseStockUnit(id);
            return response;
        }

        // ALTERNATE UNIT FUNCTIONS
        const serializeAlternateUnit = (alternateStockUnit)=> {
            if (alternateStockUnit) {
                return {
                    name: alternateStockUnit.name,
                    abbrev: alternateStockUnit.abbrev,
                    plural_name: alternateStockUnit.pluralName,
                    base_stock_units: Array.from(alternateStockUnit.baseStockUnitIds)
                };
            }
        }
        const deserializeAlternateUnit = (json)=> {
            if (json) {
                return {
                    id: json.id, name: json.name,
                    abbrev: json.abbrev, pluralName: json.plural_name,
                    pluralAbbrev: json.plural_abbrev,
                    isEditable: json.is_editable,
                    baseStockUnitIds: json.base_stock_units
                        .map(unit=> unit.id)
                };
            }
        }
        const retrieveAlternateUnit = async (id)=> {
            const response = await AlternateStockUnitApi.retrieveAlternateStockUnit(id);
            return deserializeAlternateUnit(response);
        }
        const createAlternateUnit = async(altStockUnit)=> {
            const request = serializeAlternateUnit(altStockUnit);
            const response = await AlternateStockUnitApi.createAlternateStockUnit(request);
            return deserializeAlternateUnit(response);
        }
        const updateAlternateUnit = async(id, altStockUnit)=> {
            const request = serializeAlternateUnit(altStockUnit);
            const response = await AlternateStockUnitApi.updateAlternateStockUnit(id, request);
            return deserializeAlternateUnit(response);
        }
        const deleteAlternateUnit = async(id)=> {
            const response = await AlternateStockUnitApi.deleteAlternateStockUnit(id);
            return response;
        }

        return {
            bsu, asu, deleteDialog
        }
    }
}
</script>

<style scoped>
@layer components {
    .row-disabled {
        @apply text-black text-opacity-50 cursor-not-allowed;
    }
}
</style>