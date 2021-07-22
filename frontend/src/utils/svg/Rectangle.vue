<template>
    <svg>
        <defs> 
            <pattern id="diagonal-hatch" 
                patternUnits="userSpaceOnUse" 
                width="1" height="1"
                patternTransform="rotate(-45)" >
                <path d="M 0,0 l 1,0" 
                    :stroke="'pink'"
                    :stroke-width="1"/>
            </pattern>
        </defs>
        <rect :x="$props.x" :y="$props.y" 
            :width="$props.width" :height="$props.height" 
            :style="state.style" />
    </svg>
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
        pattern: {
            type: String,
            required: false,
            default: null,
            validator: (value) => {
                return ['diagonal-hatch', 'cross-hatch'].includes(value)
            }
        },
    },
    setup(props){
        const state = reactive({
            style: computed(()=> ({
                fill: props.pattern? 
                    `url(#${props.pattern})` : props.fill,
                stroke: props.stroke,
                strokeWidth: props.strokeWidth || 1,
                'vector-effect': 'non-scaling-stroke'
            })),
            patternStyle: {}
        });


        return {
            state
        }
    }
}
</script>