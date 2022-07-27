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
import {find, orderBy} from 'lodash';

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
                items: [],
                lookupText: '',
            },
            meta: {
                materialChoicesContainer: [],
                materialChoices: computed(()=> {
                    const sorted = orderBy(
                        state.meta.materialChoicesContainer,
                        ['label'], ['asc']);
                    return sorted;
                })
            },
            select: (value) => {
                state.materialForm.items = value;
                state.emitInput();
            },
            addMaterialChoices: (choices) => {
                choices.forEach(choice => {
                    const found = find(
                        state.meta.materialChoicesContainer, 
                        {value: choice.value});
                    if (!found) {
                        state.meta.materialChoicesContainer.push(choice);
                    }
                })
            },
            clearMaterialForm: ()=> {
                state.materialForm = {
                    items: [],
                    lookupText: '',
                }
            },
            lookupMaterials: (lookupText)=> {
                state.materialForm.lookupText = lookupText;
                listMaterials(lookupText);
            },
            emitInput: ()=> {
                let materialList = state.meta.materialChoices
                    .filter(x => state.materialForm.items.includes(x.value))
                    .map(y => {
                        const existing = props.value.find(z => z.item == y.value);
                        const materialOption = {
                            id: existing? existing.id : null, 
                            item: y.value, 
                            label: y.label,
                            type: y.type
                        };
                        return materialOption;
                    });
                emit('input', materialList);
            },

        });

        const listMaterials = async (search=null) => { 
            const filter = {
                type: state.materialType || '',
            }
            const response = await ItemApi.listItems(5, 0, search, filter);
            if (response) {
                let choices = [];
                choices = response.results.map( x => ({
                    id: null,
                    label: x.full_name, 
                    value: x.id,
                    type: x.type, 
                }));
                state.addMaterialChoices(choices);
            }
        }

        watch(()=> state.materialType, ()=> {
            listMaterials();
        });

        watch(()=> props.value, async ()=> {
            if (props.value && props.value.length > 0) {
                state.materialForm.items = props.value.map(x => x.item);
                const choices = props.value.map(x => ({
                    id: x.id,
                    label: x.label, 
                    value: x.item,
                    type: x.type}));
                state.addMaterialChoices(choices);
            }
            if (state.meta.materialChoicesContainer.length == props.value.length) {
                await listMaterials();
            }
        });

        return {
            state, listMaterials
        }
    }
}
</script>