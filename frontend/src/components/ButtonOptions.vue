<template>
    <div ref="base" v-click-outside="()=> state.toggle(false)">
        <div class="cursor-pointer flex hover:text-secondary"
            :class="$props.labelPosition == 'right' ? 'flex-row-reverse' : 'flex-row'"
            @click="()=> state.toggle()">
            <span v-if="$props.label"
                class="my-auto px-1 font-bold">
                {{$props.label}}
            </span>
            <span v-if="$props.icon"
                class="my-auto px-1 material-icons">
                {{$props.icon}}
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