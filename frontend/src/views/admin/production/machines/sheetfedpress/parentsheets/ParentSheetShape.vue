<template>
    <svg :viewBox="`0 0 ${state.viewBoxWidth} ${state.viewBoxLength}`">
        <svg :viewBox="`${-state.offsetX} ${-state.offsetY} ${state.viewBoxWidth} ${state.viewBoxLength}`">
            <Rectangle 
                :width="$props.width"
                :height="$props.length"
                stroke="lightgray" fill="white"/>
            <Line v-if="$props.paddingTop > 0" 
                :stroke="state.paddingStroke" 
                :stroke-width="state.paddingStrokeWidth" dashed
                :x1="0" :y1="$props.paddingTop"
                :x2="$props.width" :y2="$props.paddingTop"/>
            <Line v-if="$props.paddingLeft"
                :stroke="state.paddingStroke" 
                :stroke-width="state.paddingStrokeWidth" dashed
                :x1="$props.paddingLeft" :y1="0"
                :x2="$props.paddingLeft" :y2="$props.length"/>
            <Line v-if="$props.paddingBottom"
                :stroke="state.paddingStroke" 
                :stroke-width="state.paddingStrokeWidth" dashed
                :x1="0" :y1="$props.length - $props.paddingBottom"
                :x2="$props.width" :y2="$props.length - $props.paddingBottom"/>
            <Line v-if="$props.paddingRight"
                :stroke="state.paddingStroke" 
                :stroke-width="state.paddingStrokeWidth" dashed
                :x1="$props.width - $props.paddingRight" :y1="0"
                :x2="$props.width - $props.paddingRight" :y2="$props.length"/>
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
import Line from '@/utils/svg/Line.vue';
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
        displayLabel: Boolean
    },
    components: {
        Rectangle, Line, LineMeasure
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