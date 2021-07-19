<template>
    <line 
        :x1="$props.x1" :y1="$props.y1" 
        :x2="$props.x2" :y2="$props.y2" 
        :style="state.style" />
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
        strokeWidth: {type: Number, default: 1},
        dashed: Boolean
    },
    setup(props){
        const state = reactive({
            style: computed(()=>({
                stroke: props.stroke,
                strokeWidth: props.strokeWidth,
                'stroke-dasharray': props.dashed ? '4,2' : 'none',
                'vector-effect': 'non-scaling-stroke'
            }))
        });
        return {
            state
        }
    }
}
</script>