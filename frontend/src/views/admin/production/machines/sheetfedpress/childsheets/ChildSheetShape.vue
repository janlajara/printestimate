<template>
    <svg :viewBox="`${$props.x} ${$props.y} ${state.viewBoxWidth} ${state.viewBoxLength}`">
        <svg>
            <Rectangle 
                :width="$props.width"
                :height="$props.length"
                :stroke="$props.stroke" 
                :stroke-width="1"
                :fill="$props.fill"/>
            <slot/>
        </svg>
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
        <svg :width="$props.width" :height="$props.length"
                :viewBox="`0 0 ${$props.width} ${$props.length}`">
            <text :id="state.text.id" v-if="$props.text"
                    :x="state.text.x" :y="state.text.y"
                    :font-size="state.text.size"
                    fill="#7e7e7e"
                    font-weight="bold">
                {{$props.text}}
            </text>
        </svg>
    </svg>
</template>
<script>
import Rectangle from '@/utils/svg/Rectangle.vue';
import Line from '@/utils/svg/Line.vue';

import {reactive, computed, onMounted} from 'vue';
import { v4 as uuid } from 'uuid';

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
        text: [String, Number],
        textSize: {type: Number, default: 1.5},
        fill: {type: String, default: 'white'},
        stroke: {type: String, default: 'darkgray'}
    },
    components: {
        Rectangle, Line
    },
    setup(props) {
        const state = reactive({
            marginStroke: 'pink',
            marginStrokeWidth: 1,
            offsetX: props.displayLabel? 2: 0,
            offsetY: props.displayLabel? 2: 0,
            viewBoxWidth: computed(()=>  props.viewBoxWidth || props.width),
            viewBoxLength: computed(()=> props.viewBoxLength || props.length),
            text: {
                id: `text-${uuid()}`, 
                size: props.textSize,
                offsetX: 0,
                offsetY: 0,
                x: computed(()=> {
                    return (props.width / 2) - state.text.offsetX
                }), 
                y: computed(()=> {
                    return (props.length / 2) + state.text.offsetY
                }),
            }
        });

        onMounted(()=> {
            let textElem = document.getElementById(state.text.id);
            if (textElem) {
                let textBbox = textElem.getBBox();
                state.text.offsetX = textBbox.width / 2;
                state.text.offsetY = textBbox.height / 4;
            }
        })

        return {
            state
        }
    }
}
</script>