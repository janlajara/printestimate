<template>
    <svg :viewBox="`-${$props.x} -${$props.y} ${state.viewBoxWidth} ${state.viewBoxLength}`">
        <Rectangle 
            :width="$props.width"
            :height="$props.length"
            stroke="lightgray" fill="white"/>
        <Line v-if="$props.marginTop > 0" 
            :stroke="state.marginStroke" 
            :stroke-width="state.marginStrokeWidth" dashed
            :x1="0" :y1="$props.marginTop"
            :x2="$props.width" :y2="$props.marginTop"/>
        <Line v-if="$props.marginLeft"
            :stroke="state.marginStroke" 
            :stroke-width="state.marginStrokeWidth" dashed
            :x1="$props.marginLeft" :y1="0"
            :x2="$props.marginLeft" :y2="$props.length"/>
        <Line v-if="$props.marginBottom"
            :stroke="state.marginStroke" 
            :stroke-width="state.marginStrokeWidth" dashed
            :x1="0" :y1="$props.length - $props.marginBottom"
            :x2="$props.width" :y2="$props.length - $props.marginBottom"/>
        <Line v-if="$props.marginRight"
            :stroke="state.marginStroke" 
            :stroke-width="state.marginStrokeWidth" dashed
            :x1="$props.width - $props.marginRight" :y1="0"
            :x2="$props.width - $props.marginRight" :y2="$props.length"/>
        <text :x="(($props.width) / 2) - ($props.width * 0.25 / 4)" 
            :y="($props.length) / 2 + ($props.length * 0.25 / 4)"
            :font-size="$props.length * 0.25">
            {{$props.text}}
        </text>
    </svg>
</template>
<script>
import Rectangle from '@/utils/svg/Rectangle.vue';
import Line from '@/utils/svg/Line.vue';

import {reactive, computed} from 'vue';

export default {
    props: {
        x: {type: Number, default: 0},
        y: {type: Number, default: 0},
        width: {type: Number, default: 0},
        length: {type: Number, default: 0},
        marginTop: {type: Number, default: 0},
        marginRight: {type: Number, default: 0},
        marginBottom: {type: Number, default: 0},
        marginLeft: {type: Number, default: 0},
        viewBoxWidth: {type: Number, default: null},
        viewBoxLength: {type: Number, default: null},
        text: [String, Number]
    },
    components: {
        Rectangle, Line
    },
    setup(props) {
        const state = reactive({
            marginStroke: 'pink',
            marginStrokeWidth: 2,
            offsetX: props.displayLabel? 2: 0,
            offsetY: props.displayLabel? 2: 0,
            viewBoxWidth: computed(()=>  props.viewBoxWidth || props.width),
            viewBoxLength: computed(()=> props.viewBoxLength || props.length)
        });
        return {
            state
        }
    }
}
</script>