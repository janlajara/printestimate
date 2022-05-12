<template>
    <div>
        <div class="grid gap-4 md:grid-cols-3">
            <InputTextLookup name="Item" multiple 
                :disabled="state.materialType == ''"
                placeholder="Search..." class="flex-grow md:col-span-2"
                :text="state.materialForm.lookupText"
                @select="value => state.select(value)"
                @input="value => state.lookupMaterials(value)"
                :options="state.meta.materialChoices.map( option => ({
                    value: option.value,
                    title: option.label,
                    subtitle: option.type,
                    isSelected: state.materialForm.items.includes(option.value)
                }))"/>
        </div>
    </div>
</template>
<script>
import InputTextLookup from '@/components/InputTextLookup.vue';

import {reactive, computed, watch} from 'vue';
import {ItemApi} from '@/utils/apis.js';
import {differenceWith, isEqual} from 'lodash';

export default {
    components: {
        InputTextLookup
    },
    props: {
        materialType: String,
        value: Array
    },
    emits: ['input'],
    setup(props, {emit}) {
        const state = reactive({
            materialType: computed(()=> props.materialType),
            materialForm: {
                id: null,
                items: [],
                lookupText: '',
            },
            meta: {
                selectedMaterialChoices: [],
                materialChoices: [],
            },
            select: (value) => {
                state.materialForm.items = value;
                const choices = state.materialForm.items.map(x => 
                    state.meta.materialChoices.find(y => y.value == x));
                state.meta.selectedMaterialChoices = choices;
                state.emitInput();
            },
            clearMaterialForm: ()=> {
                state.materialForm = {
                    id: null,
                    items: [],
                    lookupText: null,
                }
            },
            lookupMaterials: (lookupText)=> {
                state.materialForm.lookupText = lookupText;
                listMaterials(lookupText);
            },
            emitInput: ()=> {
                let materialList = [];
                if (state.materialForm.items.length > 0) {
                    materialList = state.materialForm.items.map(x => {
                        const choice = state.meta.materialChoices.find( y => y.value == x);
                        const existing = props.value.find(z => z.item == x);
                        if (choice) {
                            const materialOption = {
                                id: existing? existing.id : null, 
                                item: x, label: choice.label
                            };
                            return materialOption;
                        }
                    });
                }
                emit('input', materialList);
            }
        }); 

        const listMaterials = async (search=null) => { 
            const filter = {
                type: state.materialType || '',
            }
            const response = await ItemApi.listItems(5, 0, search, filter);
            if (response) {
                let choices = [];
                choices = response.results.map( x => ({
                    label: x.full_name, value: x.id,
                    type: x.type, 
                }));
                const toAdd = state.meta.selectedMaterialChoices;
                const diff = differenceWith(toAdd, choices, isEqual);
                state.meta.materialChoices = diff.concat(choices);
            }
        } 
        watch(()=> props.value, async ()=> {
            if (props.value.length > 0) {
                state.materialForm.items = props.value.map(x => 
                    x? x.item : null);
                await listMaterials();
                const toAdd = props.value.map(x => ({
                    label: x.label, value: x.item,
                    type: x.type
                }));
                const ids = new Set(state.meta.materialChoices.map(x => x.value));
                state.meta.materialChoices = [...state.meta.materialChoices, 
                    ...toAdd.filter(x => !ids.has(x.value))]; 
            }
        });
        watch(()=> state.materialType, (type)=> {
            state.materialForm.lookupText = null;
            const choices = state.meta.materialChoices;
            if (choices && choices.length > 0 && choices[0].type != type) {
                listMaterials();
            }
        });

        return {
            state, listMaterials
        }
    }
}
</script>