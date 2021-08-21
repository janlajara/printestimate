<template>
    <div>
        <div class="grid gap-4 md:grid-cols-3">
            <InputTextLookup name="Item" multiple
                placeholder="Search..." class="flex-grow md:col-span-2"
                :text="state.materialForm.lookupText"
                @select="value => {
                    state.select(value)
                }"
                @input="value => {
                    state.lookupMaterials(value);
                }"
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

import {reactive, computed, watch, onBeforeMount} from 'vue';
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
                        if (choice) {
                            const materialOption = {
                                id: choice.id, item: x, label: choice.label
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
        watch(()=> props.value, ()=> {
            if (props.value.length > 0) {
                state.materialForm.items = props.value.map(x => 
                    x? x.item : null);
            }
        });
        watch(()=> state.materialType, ()=> {
            state.materialForm.lookupText = null;
            //listMaterials();
        });
        onBeforeMount(listMaterials)

        return {
            state, listMaterials
        }
    }
}
</script>