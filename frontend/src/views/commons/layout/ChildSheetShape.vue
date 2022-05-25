<template>
    <svg :viewBox="`-${$props.x} -${$props.y} ${state.viewBoxWidth} ${state.viewBoxLength}`">
        <svg>
            <Rectangle 
                :width="state.totalWidth"
                :height="state.totalLength"
                :stroke="$props.stroke" 
                :stroke-width="1"
                :fill="$props.fill"/>
            <slot/>
        </svg>
        <Line v-if="$props.marginTop > 0" 
            :stroke="state.marginStroke" 
            :stroke-width="state.marginStrokeWidth" dashed
            :x1="0" :y1="$props.marginTop"
            :x2="state.totalWidth" :y2="$props.marginTop"/>
        <Line v-if="$props.marginLeft"
            :stroke="state.marginStroke" 
            :stroke-width="state.marginStrokeWidth" dashed
            :x1="$props.marginLeft" :y1="0"
            :x2="$props.marginLeft" :y2="state.totalLength"/>
        <Line v-if="$props.marginBottom"
            :stroke="state.marginStroke" 
            :stroke-width="state.marginStrokeWidth" dashed
            :x1="0" :y1="state.totalLength - $props.marginBottom"
            :x2="state.totalWidth" :y2="state.totalLength - $props.marginBottom"/>
        <Line v-if="$props.marginRight"
            :stroke="state.marginStroke" 
            :stroke-width="state.marginStrokeWidth" dashed
            :x1="state.totalWidth - $props.marginRight" :y1="0"
            :x2="state.totalWidth - $props.marginRight" :y2="state.totalLength"/>
        <svg :width="state.totalWidth" :height="state.totalLength"
                :viewBox="`0 0 ${state.totalWidth} ${state.totalLength}`">
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
            marginX: computed(()=> (props.marginRight + props.marginLeft)),
            marginY: computed(()=> (props.marginTop + props.marginBottom)),
            totalWidth: computed(()=> props.width + state.marginX),
            totalLength: computed(()=> props.length + state.marginY),
            offsetX: props.displayLabel? 2: 0,
            offsetY: props.displayLabel? 2: 0,
            viewBoxWidth: computed(()=>  props.viewBoxWidth || state.totalWidth),
            viewBoxLength: computed(()=> props.viewBoxLength || state.totalLength),
            text: {
                id: `text-${uuid()}`, 
                size: props.textSize,
                offsetX: 0,
                offsetY: 0,
                x: computed(()=> {
                    return (state.totalWidth/ 2) - state.text.offsetX
                }), 
                y: computed(()=> {
                    return (state.totalLength / 2) + state.text.offsetY
                }),
            }
        });

        const adjustOffset = ()=> {
            let textElem = document.getElementById(state.text.id);
            if (textElem) {
                let textBbox = textElem.getBBox();
                state.text.offsetX = textBbox.width / 2;
                state.text.offsetY = textBbox.height / 4;
            }
        }

        onMounted(adjustOffset);

        return {
            state
        }
    }
}
</script>