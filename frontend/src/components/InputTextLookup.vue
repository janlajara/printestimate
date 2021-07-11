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
        <div class="relative w-full " :class="bgStyle" 
            v-click-outside="()=> lookup.toggle(false)">
            <div v-if="lookup.selected"
                class="flex h-9">
                <span class="flex my-auto mx-3 text-xs">
                    {{lookup.selected}}
                    <span @click="lookup.clearSelect" 
                        class="my-auto material-icons ml-2 text-xs 
                        cursor-pointer text-gray-400 hover:text-red-400">
                        close</span>
                </span>
            </div> 
            <div v-else>
                <input type="text" class="rounded border-0 bg-transparent shadow-sm w-full" 
                    :disabled="$props.disabled"
                    @click="event => {
                        $emit('input', event.target.value);
                        lookup.toggle(true);
                    }"
                    @input="event => {
                        $emit('input', event.target.value);
                        lookup.toggle(true);
                    }"
                    :placeholder="$props.placeholder" 
                    :value="$props.value"
                    :class="[sizeStyle]"/>
                <div class="bg-white rounded absolute shadow-md w-full mt-1 z-10 max-h-44 overflow-y-auto"
                    v-if="lookup.isOpen">
                    <div v-for="(option, index) in $props.options" :key="index"
                        class="p-2 hover:bg-secondary-light hover:bg-opacity-20 text-sm cursor-pointer"
                        @click="()=> lookup.select(option.value, option.title + ' : ' + option.subtitle)">
                        <dt class="text-sm flex justify-between">
                            <span class="font-bold">{{option.title}}</span>
                            <span class="text-right">{{option.figure}}</span>
                        </dt>
                        <dd class="text-xs flex justify-between">
                            <span class="text-gray-400 capitalize">{{option.subtitle}}</span>
                            <span class="text-gray-400 text-right">{{option.timestamp}}</span>
                        </dd>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
import {reactive, watch} from 'vue';

export default {
    props: {
        name: String,
        value: String,
        options: Array,
        required: Boolean,
        disabled: Boolean,
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
            selected: null,
            toggle: (value) => {
                lookup.isOpen = value;
            },
            select: (value, label) => {
                lookup.selected = label;
                lookup.toggle(false);
                emit('select', value);
            },
            clearSelect: ()=> {
                lookup.selected = null;
                emit('select', '');
            }
        })
        watch(()=> props.value, 
            lookup.clearSelect
        )
        return {
            bgStyle: bgs[props.bg],
            sizeStyle: sizes[props.size],
            lookup
        }
    }
}
</script>