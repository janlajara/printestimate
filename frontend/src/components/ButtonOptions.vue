<template>
    <div v-click-outside="()=> state.toggle(false)">
        <div ref="base" class="cursor-pointer hover:text-secondary inline"
            @click="()=> state.toggle()">
            <span v-show="$props.label && 
                ($props.labelPosition == null || $props.labelPosition == 'left')"
                class="inline-block align-middle px-1 font-bold">
                {{$props.label}}
            </span>
            <span v-show="$props.icon"
                class="inline-block align-middle px-1 material-icons">
                {{$props.icon}}
            </span>
            <span v-show="$props.label && $props.labelPosition == 'right'"
                class="inline-block align-middle px-1 font-bold">
                {{$props.label}}
            </span>
        </div>
        <div ref="dropdown" v-if="state.isRevealed" 
            :style="`left: ${state.dropdown.x}px;`"
            @click="()=> state.toggle(false)"
            class="shadow-md rounded-md bg-white absolute w-44 mt-1 z-10">
            <slot/>
        </div>
    </div>
</template>
<script>
import {reactive, ref, computed} from 'vue';

export default {
    emits: ['click'],
    props: {
        icon: String,
        label: String,
        labelPosition: {
            type: String,
            validator: (value) => {
                return ['left', 'right'].indexOf(value) !== -1
            }
        }
    },
    setup() {
        const state = reactive({
            isRevealed: false,
            toggle: value => { 
                let isRevealed = value;
                if (value == null) isRevealed = !state.isRevealed;
                state.isRevealed = isRevealed;
            },
            dropdown: {
                x: computed(()=> {
                    if (base.value && dropdown.value) {
                        const baseRect = base.value.getBoundingClientRect();
                        return baseRect.x - (dropdown.value.clientWidth - baseRect.width);
                    } else {
                        return 0;
                    }
                })
            }
        });
        const base = ref(null);
        const dropdown = ref(null);
        return {
            state, base, dropdown
        }
    }
}
</script>