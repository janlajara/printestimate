<template>
    <rect 
        :x="$props.x" :y="$props.y" 
        :width="$props.width" :height="$props.height" 
        :style="state.style" />
</template>
<script>
import {reactive, computed} from 'vue';

export default {
    props: {
        x: {type: Number, default: 0}, 
        y: {type: Number, default: 0},
        width: {type: Number, default: 0}, 
        height: {type: Number, default: 0},
        fill: {type: String, default: "transparent"},
        stroke: {type: String, default: "none"},
        strokeWidth: {type: Number, default: 1},
    },
    setup(props){
        const state = reactive({
            style: computed(()=> ({
                fill: props.fill,
                stroke: props.stroke,
                strokeWidth: props.strokeWidth || 1,
                'vector-effect': 'non-scaling-stroke'
            }))
        });
        return {
            state
        }
    }
}
</script>