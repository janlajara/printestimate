<template>
    <svg>
        <Rectangle 
            :width="$props.width"
            :height="$props.length"
            stroke="lightgray" fill="white"/>
        <Line :stroke="state.paddingStroke" 
            :stroke-width="state.paddingStrokeWidth" dashed
            :x1="0" :y1="$props.paddingTop"
            :x2="$props.width" :y2="$props.paddingTop"/>
        <Line :stroke="state.paddingStroke" 
            :stroke-width="state.paddingStrokeWidth" dashed
            :x1="$props.paddingLeft" :y1="0"
            :x2="$props.paddingLeft" :y2="$props.length"/>
        <Line :stroke="state.paddingStroke" 
            :stroke-width="state.paddingStrokeWidth" dashed
            :x1="0" :y1="$props.length - $props.paddingBottom"
            :x2="$props.width" :y2="$props.length - $props.paddingBottom"/>
        <Line :stroke="state.paddingStroke" 
            :stroke-width="state.paddingStrokeWidth" dashed
            :x1="$props.width - $props.paddingRight" :y1="0"
            :x2="$props.width - $props.paddingRight" :y2="$props.length"/>
    </svg>
</template>
<script>
import Rectangle from '@/utils/svg/Rectangle.vue';
import Line from '@/utils/svg/Line.vue';

import {reactive} from 'vue';

export default {
    props: {
        data: Object,
        width: {type: Number, default: 0},
        length: {type: Number, default: 0},
        paddingTop: {type: Number, default: 0},
        paddingRight: {type: Number, default: 0},
        paddingBottom: {type: Number, default: 0},
        paddingLeft: {type: Number, default: 0},
    },
    components: {
        Rectangle, Line
    },
    setup() {
        const state = reactive({
            paddingStroke: 'pink',
            paddingStrokeWidth: 2,
        });
        return {
            state
        }
    }
}
</script>