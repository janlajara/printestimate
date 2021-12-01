<template>
    <div class="mt-2 bg-gray-200 px-4 py-4 rounded-md">
        <div v-if="state.parentToRunsheet != null">
            <Svg :svg-height="250"
                :view-box-width="state.parentToRunsheet.bin.width" 
                :view-box-height="state.parentToRunsheet.bin.length">
                <Rectangle 
                    :width="state.parentToRunsheet.bin.width"
                    :height="state.parentToRunsheet.bin.length"
                    stroke="#838383" :stroke-width="2" 
                    pattern="diagonal-hatch"
                    pattern-color="#d3677b"
                    pattern-fill="#cecece"/>
                <ParentSheetShape :key="pkey"
                    v-for="(runsheet, pkey) in state.parentToRunsheet.layouts"
                    :view-box-width="state.parentToRunsheet.bin.width"
                    :view-box-length="state.parentToRunsheet.bin.length"
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
                            :view-box-width="state.parentToRunsheet.bin.width"
                            :view-box-length="state.parentToRunsheet.bin.length">
                            <!--template v-if="state.cutsheetToTrimsheet">
                                <Rectangle 
                                    :key="tkey"
                                    v-for="(trimsheet, tkey) in state.cutsheetToTrimsheet.layouts"
                                    :x="runsheet.is_rotated && cutsheet.is_rotated? 
                                        trimsheet.x : trimsheet.y"
                                    :y="runsheet.is_rotated && cutsheet.is_rotated? 
                                        trimsheet.y : trimsheet.x"
                                    :width="runsheet.is_rotated && cutsheet.is_rotated? 
                                        trimsheet.width : trimsheet.length"
                                    :height="runsheet.is_rotated && cutsheet.is_rotated? 
                                        trimsheet.length : trimsheet.width"
                                    stroke="grey" :stroke-width="1" fill="white"/>
                            </template-->
                        </ChildSheetShape>
                    </template>
                </ParentSheetShape>
            </Svg>
        </div>
    </div>
</template>
<script>
import Svg from '@/utils/svg/Svg.vue';
import Rectangle from '@/utils/svg/Rectangle.vue';
import ParentSheetShape from '@/views/admin/production/machines/sheetfedpress/parentsheets/ParentSheetShape.vue';
import ChildSheetShape from '@/views/admin/production/machines/sheetfedpress/childsheets/ChildSheetShape.vue';

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
            cutsheetToTrimsheet: computed(()=> findLayout('Cutsheet-to-trimsheet'))
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