<template>
    <div :class="$props.name ? 'mt-2' : ''">
        <label v-if="$props.name">
            <span class="text-sm font-medium">
                {{$props.name}}</span>
            <span v-if="$props.required" 
                class="text-secondary-light">*</span>
            <span v-if="$props.disabled" 
                class="material-icons text-sm text-secondary-light">lock</span>
        </label>
        <div class="relative w-full" :class="bgStyle" 
            v-click-outside="()=> lookup.toggle(false)">
            <div v-if="lookup.selected.length > 0"
                class="grid">
                <span v-for="(obj, key) in lookup.selectedObjects" :key="key"
                    class="flex my-auto mx-3 text-xs py-2">
                    <span v-if="obj">
                        {{obj.title}} : {{obj.subtitle}}
                        <span @click="() => lookup.clearSelect(obj.value)" 
                            class="my-auto material-icons ml-2 text-xs 
                            cursor-pointer text-gray-400 hover:text-red-400">
                            close</span>
                    </span>
                </span>
            </div> 
            <div v-if="lookup.isEditable">
                <input type="text" class="rounded border-0 bg-transparent shadow-sm w-full" 
                    :disabled="$props.disabled"
                    @click="event => {
                        lookup.toggle(true);
                    }"
                    @input="event => {
                        lookup.emitOnInput(event);
                    }"
                    :placeholder="$props.placeholder" 
                    :value="$props.text"
                    :class="[sizeStyle]"/>
                <span class="material-icons absolute right-2 top-1">search</span>
                <div class="bg-white rounded absolute shadow-md w-full mt-1 z-10 max-h-44 overflow-y-auto"
                    v-if="lookup.isOpen">
                    <div :key="index" class="p-2 hover:bg-secondary-light hover:bg-opacity-20 text-sm cursor-pointer"
                        v-for="(option, index) in lookup.options.filter(x => !x.isSelected)" 
                        @click="()=> lookup.select(option.value)">
                        <dt class="text-sm flex justify-between">
                            <span class="font-bold">{{option.title}}</span>
                            <span class="text-right">{{option.figure}}</span>
                        </dt>
                        <dd class="text-xs flex justify-between">
                            <span class="text-gray-400 capitalize">{{option.subtitle}}</span>
                            <span class="text-gray-400 text-right">{{option.timestamp}}</span>
                        </dd>
                    </div>
                    <div v-if="lookup.options.length == 0" class="p-2 text-sm">
                        <dt class="text-sm flex justify-between">
                            <span class="italic">No results found</span>
                        </dt>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import {reactive, computed, watch} from 'vue';
import {debounce} from 'lodash';

export default {
    props: {
        name: String,
        text: String,
        options: {
            type: Array,
            default: ()=>[]
            // value, title, subtitle, figure, selected
        },
        required: Boolean,
        disabled: Boolean,
        multiple: Boolean,
        placeholder: String,
        bg: {
            type: String,
            default: 'regular',
            validator: (value) => {
                return ['none', 'white', 'regular'].indexOf(value) !== -1
            }
        },
        size: {
            type: String,
            default: 'regular',
            validator: (value) => {
                return ['small', 'large', 'regular'].indexOf(value) !== -1
            }
        },
    },
    emits: ['input', 'select'],
    setup(props, {emit}) {
        const bgs = {
            'none': 'bg-transparent border-gray-400 border-b',
            'white': 'bg-white rounded',
            'regular': 'bg-gray-200 rounded',
        }
        const sizes = {
            'small': 'text-xs',
            'regular': 'text-sm',
            'large': 'text-lg'
        }
        const lookup = reactive({
            isOpen: false,
            isEditable: computed(()=> 
                lookup.selected.length == 0 ||
                (props.multiple)),
            selected: [],
            selectedObjects: computed(()=> 
                lookup.selected.map(x => 
                    lookup.options.find(y => y.value == x))),
            options: [],
            toggle: (value) => {
                lookup.isOpen = value;
            },
            select: (value) => {
                if (!props.multiple) {
                    lookup.selected = [value]
                    lookup.toggle(false);
                    emit('select', value);
                } else {
                    lookup.selected.push(value);
                    emit('select', lookup.selected)
                }
            },
            clearSelect: (value=null)=> {
                if (value) {
                    const index = lookup.selected.indexOf(value);
                    lookup.selected.splice(index, 1)
                } else {
                    lookup.selected = [];
                }
                emit('select', (!props.multiple)? '': lookup.selected);
            },
            emitOnInput: debounce((event)=> {
                emit('input', event.target.value);
                lookup.toggle(true);}, 500)
        })
        watch(()=> props.options, ()=> {
            lookup.options = props.options;
            lookup.selected = props.options
                .filter(x => x.isSelected)
                .map(x => x.value);
        });
        return {
            bgStyle: bgs[props.bg],
            sizeStyle: sizes[props.size],
            lookup
        }
    }
}
</script>