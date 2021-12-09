<template>
    <div class="mt-2 bg-gray-200 px-4 py-4 rounded-md">
        <Svg :svg-height="250"
            :view-box-width="state.svgRect.width" 
            :view-box-height="state.svgRect.length">
            <Rectangle 
                :width="state.svgRect.width"
                :height="state.svgRect.length"
                stroke="#838383" :stroke-width="2" 
                pattern="diagonal-hatch"
                pattern-color="#d3677b"
                pattern-fill="#cecece"/>
            <!-- if layout consts of parentsheet, runsheet and childsheet -->
            <template v-if="state.parentToRunsheet">
                <ParentSheetShape 
                    :key="pkey"
                    v-for="(runsheet, pkey) in state.parentToRunsheet.layouts"
                    :view-box-width="state.svgRect.width"
                    :view-box-length="state.svgRect.length"
                    :x="runsheet.x" :y="runsheet.y"
                    :width="runsheet.width"
                    :length="runsheet.length"
                    stroke="#838383" 
                    :stroke-width="2"
                    pattern="diagonal-hatch"
                    pattern-fill="white"
                    :padding-top="runsheet.padding_top"
                    :padding-right="runsheet.padding_right"
                    :padding-bottom="runsheet.padding_bottom"
                    :padding-left="runsheet.padding_right">
                    <template v-if="state.runsheetToCutsheet">
                        <ChildSheetShape 
                            :key="ckey" v-for="(cutsheet, ckey) in state.runsheetToCutsheet.layouts"
                            :text="(state.runsheetToCutsheet.layouts.length * pkey) + cutsheet.i"
                            stroke="#838383" stroke-width="1" fill="white"
                            :x="!runsheet.is_rotated?
                                (cutsheet.x + runsheet.x + runsheet.padding_left) :
                                (cutsheet.y + runsheet.x + runsheet.padding_left)" 
                            :y="!runsheet.is_rotated?
                                (cutsheet.y + runsheet.y + runsheet.padding_top) :
                                (cutsheet.x + runsheet.y + runsheet.padding_top)"
                            :width="!runsheet.is_rotated? 
                                cutsheet.width : cutsheet.length"
                            :length="!runsheet.is_rotated? 
                                cutsheet.length : cutsheet.width"
                            :margin-top="!runsheet.is_rotated? 
                                cutsheet.margin_top : cutsheet.margin_right"
                            :margin-right="!runsheet.is_rotated? 
                                cutsheet.margin_right : cutsheet.margin_bottom"
                            :margin-bottom="!runsheet.is_rotated? 
                                cutsheet.margin_bottom : cutsheet.margin_left"
                            :margin-left="!runsheet.is_rotated? 
                                cutsheet.margin_left : cutsheet.margin_top"
                            :view-box-width="state.svgRect.width"
                            :view-box-length="state.svgRect.length">
                        </ChildSheetShape>
                    </template>
                </ParentSheetShape>
            </template>
            <template v-else-if="state.parentToCutsheet">
                <ChildSheetShape 
                    :key="ckey" v-for="(cutsheet, ckey) in state.parentToCutsheet.layouts"
                    :text="cutsheet.i"
                    stroke="#838383" stroke-width="1" fill="white"
                    :x="cutsheet.x" :y="cutsheet.y"
                    :width="cutsheet.width" :length="cutsheet.length"
                    :margin-top="cutsheet.margin_top"
                    :margin-right="cutsheet.margin_right"
                    :margin-bottom="cutsheet.margin_bottom"
                    :margin-left="cutsheet.margin_left"
                    :view-box-width="state.svgRect.width"
                    :view-box-length="state.svgRect.length">
                </ChildSheetShape>
            </template>
        </Svg>
    </div>
</template>
<script>
import Svg from '@/utils/svg/Svg.vue';
import Rectangle from '@/utils/svg/Rectangle.vue';
import ParentSheetShape from './ParentSheetShape.vue';
import ChildSheetShape from './ChildSheetShape.vue';
 
import {reactive, computed} from 'vue';

export default {
    props: {
        layouts: {
            type: Array,
            default: ()=> []
        }
    },
    components: {
        Svg, Rectangle, ParentSheetShape, ChildSheetShape
    },
    setup(props) {
        const state = reactive({
            layouts: computed(()=> props.layouts || []),
            parentToRunsheet: computed(()=> findLayout('Parent-to-runsheet')),
            runsheetToCutsheet: computed(()=> findLayout('Runsheet-to-cutsheet')),
            parentToCutsheet: computed(()=> findLayout('Parent-to-cutsheet')),
            svgRect: computed(()=> {
                let width = 0;
                let length = 0;
                if (state.parentToRunsheet != null) {
                    width = state.parentToRunsheet.bin.width;
                    length = state.parentToRunsheet.bin.length;
                } else if (state.parentToCutsheet != null) {
                    width = state.parentToCutsheet.bin.width;
                    length =state.parentToCutsheet.bin.length;
                }
                return {width, length}
            })
        });

        const findLayout = (name) => {
            let layout = null;
            if (state.layouts.length > 0) {
                layout = state.layouts.find(x=> x.name == name)
            }
            return layout;
        }

        return {
            state
        };
    }
}
</script>