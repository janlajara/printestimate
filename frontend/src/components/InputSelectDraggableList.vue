<template>
    <div class="mt-2">
        <label class="text-sm font-medium">{{$props.name}}
          <span v-if="$props.required" class="text-secondary-light">*</span>
          <span v-if="$props.disabled" 
                class="material-icons text-sm text-secondary-light">lock</span>
        </label>
        <div class="grid md:grid-cols-2 gap-2
                rounded-md shadow-sm w-full 
                border-none bg-gray-100 text-sm">
            <div class="p-2">
                <span class="text-xs font-medium">Options:</span>
                <draggable item-key="value" 
                    :group="state.group"
                    :list="state.options">
                    <template #item="option">
                        <div class="rounded-md bg-gray-100 p-2 m-1 cursor-move">
                            <span class="material-icons text-xs my-auto">drag_indicator</span>
                            <span class="pl-1">{{option.element.label}}</span>
                        </div>
                    </template>
                </draggable>
            </div>
            <div class="bg-gray-200 p-2 relative pb-6 rounded-r-md">
                <span class="text-xs italic text-gray-400">
                    Drag option to this area</span>
                <draggable item-key="id" @change="emitInput"
                    group="choices" style="min-height: 24px"
                    :list="state.selected">
                    <template #item="option">
                        <div class="flex gap-1 rounded-md bg-gray-100 p-2 m-1 cursor-move"
                            @mouseover="option.element.showDelete = true" 
                            @mouseleave="option.element.showDelete = false">
                            <span class="material-icons text-xs my-auto">drag_indicator</span>
                            <span>{{option.element.label}}</span>
                            <span v-if="$props.clone"
                                v-show="option.element.showDelete"
                                @click="()=>remove(option.element.id)"
                                class="material-icons text-xs my-auto cursor-pointer px-1">
                                close</span>
                        </div>
                    </template>
                </draggable>
            </div>
        </div>
    </div>
</template>

<script>
import {reactive, computed, onBeforeMount, watch} from 'vue';
import draggable from 'vuedraggable';

export default {
    components: {
        draggable
    },
    props: {
        name: String,
        required: Boolean,
        disabled: Boolean,
        clone: {
            type: Boolean,
            default: true
        },
        options: {
            type: Array 
            //Array of Objects 
            //{label:String, value:number}
        },
        value: Array
    },
    emits: ['input'],
    setup(props, {emit}) {  
        const state = reactive({
            baseOptions: [],
            options: computed(()=> {
                const options = (!props.required)? 
                    [{value: null, label: ''}].concat(state.baseOptions):
                    state.baseOptions;
                return options;
            }),
            counter: 0,
            selected: [],
            group: { 
                name: 'choices', 
                put:true, pull: true }
        });

        const add = ({value, label}) => { 
            return {
                id: state.counter++,
                value, label,
                showDelete: false}
        };

        const remove = (id) => {
            const index = state.selected.findIndex(o => o.id == id);
            if (index > -1) {
                state.selected.splice(index, 1);
                emitInput();
            }
        }

        const emitInput = () => {
            const selected = state.selected.map(x => x.value);
            emit('input', selected);
        }

        const initializeSelectedOptions = () => {
            state.selected = []
            state.baseOptions = props.options.filter(prop => prop && prop.value != null);
            props.value.forEach( x => {
                const index = state.baseOptions.findIndex(y=> y.value == x);
                if (index > -1) {
                    const option = state.baseOptions[index];
                    state.selected.push(add(option))

                    // Remove item from source list if setting is not clone
                    if (!props.clone) {
                        state.baseOptions.splice(index, 1);
                    }
                }
            });
        };

        watch(()=> props.value, initializeSelectedOptions);

        onBeforeMount(()=> { 
            if (props.clone) {
                state.group.pull = 'clone';
                state.group.put = false;
            }
        });

        return {
            state, add, remove, emitInput
        }
    }
}
</script>
