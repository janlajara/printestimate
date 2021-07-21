<template>
    <Svg :svg-height="200"
        :view-box-width="$props.parentWidth" 
        :view-box-height="$props.parentLength">
        <ParentSheetShape 
            :width="$props.parentWidth"
            :length="$props.parentLength"
            :padding-top="$props.parentPaddingTop"
            :padding-right="$props.parentPaddingRight"
            :padding-bottom="$props.parentPaddingBottom"
            :padding-left="$props.parentPaddingLeft">
        </ParentSheetShape>
        <template v-if="state.rects.length > 0">
            <ChildSheetShape 
                :key="key" v-for="(rect, key) in state.rects"
                :x="rect.x + $props.parentPaddingRight" 
                :y="rect.y + $props.parentPaddingTop"
                :text="rect.i"
                :width="rect.width"
                :length="rect.length"
                :margin-top="$props.childMarginTop"
                :margin-right="$props.childMarginRight"
                :margin-bottom="$props.childMarginBottom"
                :margin-left="$props.childMarginLeft"
                :view-box-width="$props.parentWidth"
                :view-box-length="$props.parentLength"/>
        </template>
    </Svg>
</template>

<script>
import Svg from '@/utils/svg/Svg.vue';
import ParentSheetShape from '@/views/admin/production/machines/sheetfedpress/parentsheets/ParentSheetShape.vue';
import ChildSheetShape from '@/views/admin/production/machines/sheetfedpress/childsheets/ChildSheetShape.vue';

import {reactive, computed, onMounted, onUpdated} from 'vue';
import {ChildSheetApi} from '@/utils/apis.js'

export default {
    props: {
        parentWidth: {type: Number, default: 0},
        parentLength: {type: Number, default: 0},
        parentPaddingTop: {type: Number, default: 0},
        parentPaddingRight: {type: Number, default: 0},
        parentPaddingBottom: {type: Number, default: 0},
        parentPaddingLeft: {type: Number, default: 0},
        parentUom: {type: String, default: 'inch'},
        childWidth: {type: Number, default: 0},
        childLength: {type: Number, default: 0},
        childMarginTop: {type: Number, default: 0},
        childMarginRight: {type: Number, default: 0},
        childMarginBottom: {type: Number, default: 0},
        childMarginLeft: {type: Number, default: 0},
        childUom: {type: String, default: 'inch'},
    },
    components: {
        Svg, ParentSheetShape, ChildSheetShape
    },
    setup(props) {
        const state = reactive({
            childSheet: computed(()=> ({
                parent: {
                    width_value: props.parentWidth,
                    length_value: props.parentLength,
                    size_uom: props.parentUom,
                    padding_top: props.parentPaddingTop,
                    padding_right: props.parentPaddingRight,
                    padding_bottom: props.parentPaddingBottom,
                    padding_left: props.parentPaddingLeft
                },
                width_value: props.childWidth,
                length_value: props.childLength,
                size_uom: props.childUom,
                margin_top: props.childMarginTop,
                margin_right: props.childMarginRight,
                margin_bottom: props.childMarginBottom,
                margin_left: props.childMarginLeft
            })),
            childSheetLayoutRotate: null,
            childSheetLayoutNoRotate: null,
            rects: computed(()=> state.childSheetLayoutRotate ?
                state.childSheetLayoutRotate.rects : [])
        })

        const retrieveChildSheetLayout = async (sheet) => {
            if (sheet) {
                const response = await ChildSheetApi.retrieveChildSheetLayout(sheet);
                if (response) {
                    state.childSheetLayoutRotate = response.allow_rotate;
                    state.childSheetLayoutNoRotate = response.no_rotate;
                }
            }
        }

        onMounted(()=> retrieveChildSheetLayout(state.childSheet));
        onUpdated(()=> retrieveChildSheetLayout(state.childSheet));

        return {
            state
        }
    }
}
</script>