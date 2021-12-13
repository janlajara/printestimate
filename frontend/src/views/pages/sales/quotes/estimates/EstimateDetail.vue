<template>
    <Page :title="`Estimate : ${state.data.estimateCode}`">
        <hr class="my-4"/>
        <div class="flex gap-4">
            <Button color="secondary" icon="arrow_back"
                @click="()=>$router.go(-1)">Go Back</Button>
            <Button class="my-auto" icon="edit"
                @click="state.components.editModal.open"/>
            <Button icon="delete" 
                @click="state.components.deleteDialog.open"/>
            <DeleteRecordDialog 
                heading="Delete Quote"
                :is-open="state.components.deleteDialog.isOpen"
                :execute="state.components.deleteDialog.delete"
                :on-after-execute="()=>$router.go(-1)"
                @toggle="state.components.deleteDialog.toggle">
                <div>
                    Are you sure you want to delete 
                    <span class="font-bold">
                        {{state.data.estimateCode}}</span>?
                </div>
            </DeleteRecordDialog>
        </div>
        <Section>
            <DescriptionList class="md:grid-cols-3">
                <DescriptionItem  
                    name="Template" :loader="state.isProcessing" 
                    :value="`[${state.data.templateCode}] ${state.data.templateName}`"/>
                <DescriptionItem :loader="state.isProcecssing"
                    name="Description" :value="state.data.templateDescription"/>
            </DescriptionList>
        </Section>
        <Section>
            <div class="w-full">
                <table class="table-auto w-full">
                    <thead>
                        <tr class="border-b">
                            <th class="font-bold text-lg text-left">
                                Cost Estimation</th>
                            <th v-for="(quantity, key) in state.data.quantities" :key="key"
                                class="font-bold w-40">
                                {{quantity}}
                            </th>
                        </tr>
                    </thead>

                    <!-- Rows for Bill of Materials -->
                    <thead>
                        <tr>
                            <td class="pt-4 underline col">
                                <span>Bill of Materials</span>
                            </td>
                        </tr> 
                    </thead>
                    <tbody v-for="(material, x) in state.data.billOfMaterials" :key="x"
                        class="border-b">
                        <tr class="border-b-2 border-dotted">
                            <td class="cursor-pointer" 
                                @click="()=>{material.isExpanded = !material.isExpanded}">
                                <div class="flex">
                                    <span class="material-icons text-base my-auto">
                                        {{material.isExpanded? 
                                            'expand_more' : 'chevron_right'}}</span>
                                    <div class="ml-4">
                                        <span class="text-sm inline-block align-middle">
                                            {{material.name}}</span>
                                    </div> 
                                    <div class="ml-4 flex-auto text-right">
                                        <span class="text-xs inline-block align-middle">
                                            {{formatMoney(material.rate)}} / {{material.uom}}</span>    
                                    </div>
                                </div>
                            </td>
                            <td v-for="(estimate, y) in material.estimates" :key="y">
                                <div class="text-xs grid grid-cols-2 gap-4">
                                    <div class="text-right">
                                        {{estimate.totalMaterialQuantity}}</div>
                                    <div class="text-left">
                                        {{formatMoney(material.rate * estimate.totalMaterialQuantity)}}</div>
                                </div>
                            </td>
                        </tr>
                        <tr v-show="material.isExpanded"
                            class="border-b-2 border-dotted text-gray-400">
                            <td>
                                <div class="flex">
                                    <div class="ml-8 text-sm">Stock Quantity</div>
                                    <div class="ml-4 flex-auto text-right">
                                        <span class="text-xs inline-block align-middle">
                                            {{material.rateLabel}} / {{material.uom}}</span>    
                                    </div>
                                </div>                              
                            </td>
                            <td v-for="(estimate, y) in material.estimates" :key="y">
                                <div class="text-xs grid grid-cols-2 gap-4 text-gray-400">
                                    <div class="text-right">
                                        {{estimate.estimatedMaterialQuantity}}</div>
                                    <div class="text-left">
                                        {{formatMoney(material.rate * estimate.estimatedMaterialQuantity)}}</div>
                                </div>
                            </td>
                        </tr>
                        <tr v-show="material.isExpanded"
                            class="text-gray-400">
                            <td>
                                <div class="flex">
                                    <div class="ml-8 text-sm">Spoilage ({{material.spoilageRate}}%)</div>
                                    <div class="ml-4 flex-auto text-right">
                                        <span class="text-xs inline-block align-middle">
                                            {{material.rateLabel}} / {{material.uom}}</span>    
                                    </div>
                                </div>
                            </td>
                            <td v-for="(estimate, y) in material.estimates" :key="y">
                                <div class="text-xs grid grid-cols-2 gap-4">
                                    <div class="text-right">
                                        {{estimate.spoilageMaterialQuantity}}</div>
                                    <div class="text-left">
                                        {{formatMoney(material.rate * estimate.spoilageMaterialQuantity)}}</div>
                                </div>
                            </td>
                        </tr>
                    </tbody>
                    <tfoot>
                        <tr>
                            <td>
                            </td>
                            <td v-for="(quantity, x) in state.data.quantities" :key="x">
                                <div class="text-xs grid grid-cols-2 gap-4">
                                    <div></div>
                                    <div class="underline">
                                        {{state.getMaterialTotalPriceByQuantity(quantity)}}</div>
                                </div>
                            </td>
                        </tr> 
                    </tfoot>

                    <!-- Rows for Services -->


                </table>
            </div>
        </Section>
    </Page>
    
</template>
<script>
import Page from '@/components/Page.vue';
import Button from '@/components/Button.vue';
import Section from '@/components/Section.vue';
import DeleteRecordDialog from '@/components/DeleteRecordDialog.vue';
import DescriptionList from '@/components/DescriptionList.vue';
import DescriptionItem from '@/components/DescriptionItem.vue';

import {reactive, inject} from 'vue';
import {formatQuantity, formatMoney as formatCurrency} from '@/utils/format.js'

export default {
    components: {
        Page, Button, Section, DeleteRecordDialog, DescriptionList, DescriptionItem
    },
    setup() {
        const currency = inject('currency').abbreviation
        const state = reactive({
            isProcessing: false,
            data: {
                estimateCode: 'CE-1234',
                templateCode: 'PT-9876',
                templateName: 'Carbonless Form',
                templateDescription: '8.5x11" Carbonless Form (White, Yellow, Blue)',
                quantities: [100, 200, 300],
                billOfMaterials: [
                    {name: 'Generic Carbonless White 32x24inch', 
                     rate: 30.00, rateLabel: '30.00 PHP',
                     uom: 'sheet', uomPlural: 'sheets',
                     spoilageRate: 0, isExpanded: false,
                     estimates: [
                        {itemQuantity: 100, 
                          estimatedMaterialQuantity: 300,
                          spoilageMaterialQuantity: 0,
                          totalMaterialQuantity: 300},
                        {itemQuantity: 200, 
                          estimatedMaterialQuantity: 600,
                          spoilageMaterialQuantity: 0,
                          totalMaterialQuantity: 600},
                        {itemQuantity: 300, 
                          estimatedMaterialQuantity: 900,
                          spoilageMaterialQuantity: 0,
                          totalMaterialQuantity: 900}
                     ]},
                     {name: 'Carbonless Blue 32x24', 
                     rate: 30.00, 
                     uom: 'sheet', uomPlural: 'sheets',
                     spoilageRate: 0, isExpanded: false,
                     estimates: [
                        {itemQuantity: 100, 
                          estimatedMaterialQuantity: 300,
                          spoilageMaterialQuantity: 0,
                          totalMaterialQuantity: 300},
                        {itemQuantity: 200, 
                          estimatedMaterialQuantity: 600,
                          spoilageMaterialQuantity: 0,
                          totalMaterialQuantity: 600},
                        {itemQuantity: 300, 
                          estimatedMaterialQuantity: 900,
                          spoilageMaterialQuantity: 0,
                          totalMaterialQuantity: 900}
                     ]}
                ], 
            },
            components: {
                editModal: {
                    open: ()=> {}
                },
                deleteDialog: {
                    isOpen: false,
                    toggle: value => state.components.deleteDialog.isOpen = value,
                    open: ()=> state.components.deleteDialog.toggle(true),
                    delete: ()=> {}
                }
            },
            getMaterialTotalPriceByQuantity: (quantity=0) => {
                const prices = state.data.billOfMaterials
                    .filter(x=>x.estimates.find(y=>y.itemQuantity == quantity) != null)
                    .map(x=>x.estimates.find(y=>y.itemQuantity == quantity).totalMaterialQuantity * x.rate);
                const totalPrice = prices.reduce((a,b)=> a+b, 0);
                return formatMoney(totalPrice);
            }
        });

        const formatMoney = (amount)=> {
            if (amount != null)
                return formatCurrency(amount, currency)
            else return ''
        }

        return {
            state,
            formatQuantity,
            formatMoney
        }
    }
    
}
</script>