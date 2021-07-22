<template>
    <svg :viewBox="`0 0 ${state.viewBoxWidth} ${state.viewBoxLength}`">
        <svg :viewBox="`${-state.offsetX} ${-state.offsetY} ${state.viewBoxWidth} ${state.viewBoxLength}`">
            <Rectangle 
                :width="$props.width"
                :height="$props.length"
                :stroke="state.paddingStroke" 
                :stroke-width="1"
                :fill="$props.fill"/>
            <svg>    
                <Rectangle v-if="$props.paddingTop > 0" 
                    :width="$props.width" 
                    :height="$props.paddingTop"
                    :stroke="state.paddingStroke"
                    pattern="diagonal-hatch"/>
                <Rectangle v-if="$props.paddingLeft"
                    :x="0" :y="0"
                    :width="$props.paddingLeft" 
                    :height="$props.length"
                    :stroke="state.paddingStroke"
                    pattern="diagonal-hatch"/>
                <Rectangle v-if="$props.paddingBottom"
                    :x="0" :y="$props.length - $props.paddingBottom"
                    :width="$props.width" 
                    :height="$props.paddingBottom"
                    :stroke="state.paddingStroke"
                    pattern="diagonal-hatch"/>
                <Rectangle v-if="$props.paddingRight"
                    :x="$props.width - $props.paddingRight" :y="0"
                    :width="$props.paddingRight" 
                    :height="$props.length"
                    :stroke="state.paddingStroke"
                    pattern="diagonal-hatch"/>
            </svg>
            <slot/>
        </svg>
        <template v-if="$props.displayLabel">
            <LineMeasure stroke="gray" 
                :stroke-width="1"
                :x1="state.offsetX / 2" 
                :y1="state.offsetY"
                :x2="state.offsetX / 2" 
                :y2="$props.length + state.offsetY"
                :text-size=" $props.length* 0.04"
                :text="$props.length"/>
            <LineMeasure stroke="gray" 
                :stroke-width="1"
                :x1="state.offsetX" 
                :y1="$props.length + state.offsetY * 1.5"
                :x2="state.offsetX + $props.width" 
                :y2="$props.length + state.offsetY * 1.5"
                :text-size=" $props.length* 0.04"
                :text="$props.width"/>
        </template>
    </svg>
</template>
<script>
import Rectangle from '@/utils/svg/Rectangle.vue';
import LineMeasure from '@/utils/svg/LineMeasure.vue';

import {reactive, computed} from 'vue';

export default {
    props: {
        data: Object,
        width: {type: Number, default: 0},
        length: {type: Number, default: 0},
        paddingTop: {type: Number, default: 0},
        paddingRight: {type: Number, default: 0},
        paddingBottom: {type: Number, default: 0},
        paddingLeft: {type: Number, default: 0},
        displayLabel: Boolean,
        fill: {type: String, default: 'white'}
    },
    components: {
        Rectangle, LineMeasure
    },
    setup(props) {
        const state = reactive({
            paddingStroke: 'pink',
            paddingStrokeWidth: 2,
            offsetX: props.displayLabel? 2: 0,
            offsetY: props.displayLabel? 2: 0,
            viewBoxWidth: computed(()=>  (props.width + (state.offsetX*2))),
            viewBoxLength: computed(()=> (props.length + (state.offsetY*2)))
        });
        return {
            state
        }
    }
}
</script>