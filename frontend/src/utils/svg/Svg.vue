<template>
    <svg 
        :id="state.id" :width="state.svgWidth" :height="state.svgHeight"
        :viewBox="`0 0 ${$props.viewBoxWidth} ${$props.viewBoxHeight}`">
        <slot/>
    </svg>
</template>
<script>
import {reactive, computed} from 'vue';

export default {
    props: {
        viewBoxWidth: {type: Number, default: 0}, 
        viewBoxHeight: {type: Number, default: 0},
        svgWidth: Number,
        svgHeight: Number
    },
    setup(props){
        const state = reactive({
            svgWidth: computed(()=>  props.svgWidth || '100%'),
            svgHeight: computed(()=> (props.svgWidth)? 
                '100%' : props.svgHeight || props.viewBoxHeight),
            style: []
        });
        return {
            state
        }
    }
}
</script>