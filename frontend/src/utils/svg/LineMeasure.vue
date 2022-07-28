<template>
    <svg :viewBox="`0 0 ${$props.viewBoxWidth} ${$props.viewBoxLength}`">
        <line 
            :x1="$props.x1" :y1="$props.y1" 
            :x2="$props.x2" :y2="$props.y2" 
            :style="state.style" />
        <!--circle :fill="$props.stroke" :r="$props.endpointRadius"
            :cx="$props.x1" :cy="$props.y1"/>
        <circle :fill="$props.stroke" :r="$props.endpointRadius"
            :cx="$props.x2" :cy="$props.y2"/-->
        <text :x="($props.x1 + $props.x2) / 2" 
            :y="($props.y1 + $props.y2) / 2"
            :font-size="$props.textSize" font-size-adjust="0.75">
            {{$props.text}}
        </text>
    </svg>
</template>
<script>
import {reactive, computed} from 'vue';

export default {
    props: {
        x1: {type: Number, default: 0}, 
        y1: {type: Number, default: 0},
        x2: {type: Number, default: 0}, 
        y2: {type: Number, default: 0},
        stroke: {type: String, default: 'black'},
        strokeWidth: {type: Number, default: 0.1},
        viewBoxWidth: {type: Number, default: 0}, 
        viewBoxLength: {type: Number, default: 0},
        dashed: Boolean,
        textSize: {type: Number, default: 1},
        text: {type: [Number, String]}
    },
    setup(props){
        const state = reactive({
            style: computed(()=>({
                stroke: props.stroke,
                strokeWidth: props.strokeWidth,
                //'stroke-dasharray': props.dashed ? '4,2' : 'none',
                //'vector-effect': 'non-scaling-stroke'
            })),
        });
        return {
            state
        }
    }
}
</script>