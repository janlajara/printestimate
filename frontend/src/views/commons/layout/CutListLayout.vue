<template>
    <div class="bg-gray-200 px-4 py-4 rounded-md">
        <div v-if="$props.loader" 
            class="w-full flex justify-center margin-y-auto">
            <span class="material-icons animate-spin text-secondary-light">
                autorenew
            </span>
        </div>
        <div v-else-if="state.layouts.length > 0">
            <template v-if="state.layout.count <= 100">
                <Svg :svg-height="$props.svgHeight"
                    :view-box-width="state.svgRect.width" 
                    :view-box-height="state.svgRect.length">
                    <Rectangle 
                        :width="state.svgRect.width"
                        :height="state.svgRect.length"
                        stroke="#838383" :stroke-width="2" 
                        pattern="diagonal-hatch"
                        pattern-color="#d3677b"
                        pattern-fill="#cecece"/>
                    <template v-if="state.layout.type == layout_types.SHEET_FED_PRESS_MACHINE">
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
                    <template v-else-if="state.layout.type == layout_types.ROLL_FED_PRESS_MACHINE"> 
                        <ChildSheetShape 
                            :key="ckey" v-for="(cutsheet, ckey) in state.runsheetToCutsheet.layouts"
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
                    <template v-else-if="state.layout.type == layout_types.DEFAULT">
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
            </template>
            <div v-else>
                <p class="text-sm text-gray-500 italic text-center">
                    Lay-out is too large to be displayed.</p> 
            </div>
        </div>
    </div>
</template>
<script>
import Svg from '@/utils/svg/Svg.vue';
import Rectangle from '@/utils/svg/Rectangle.vue';
import ParentSheetShape from './ParentSheetShape.vue';
import ChildSheetShape from './ChildSheetShape.vue';
 
import convert from 'convert';
import {reactive, computed, onMounted, onUpdated} from 'vue';


export const layout_types = {
    SHEET_FED_PRESS_MACHINE: 'SheetFedPressMachine',
    ROLL_FED_PRESS_MACHINE: 'RollFedPressMachine',
    DEFAULT: 'Default'
};

export default {
    props: {
        layoutType: String,
        layouts: {
            type: Object,
            default: null
        },
        svgHeight: {
            type: Number,
            default: 250
        },
        loader: Boolean
    },
    components: {
        Svg, Rectangle, ParentSheetShape, ChildSheetShape
    },
    emits: ['load'],
    setup(props, {emit}) {
        const state = reactive({
            layouts: computed(()=> props.layouts || []),
            layoutType: computed(()=> {
                let type = props.layoutType;
                if (state.layouts.length > 0 && type == null)
                    type = layout_types.DEFAULT;
                return type
            }),
            parentToRunsheet: computed(()=> findLayout('Parent-to-runsheet')),
            runsheetToCutsheet: computed(()=> findLayout('Runsheet-to-cutsheet')),
            parentToCutsheet: computed(()=> findLayout('Parent-to-cutsheet')),
            layout: computed(()=> {
                const type = state.layoutType;
                let count = 0;
                let main = null;
                if (type == layout_types.SHEET_FED_PRESS_MACHINE) {
                    main = state.parentToRunsheet;
                } else if (type == layout_types.ROLL_FED_PRESS_MACHINE) {
                    main = state.runsheetToCutsheet;
                } else {
                    main = state.parentToCutsheet;
                }
                if (main) count = main.count;
                return {
                    type, count, main
                };
            }),
            hasRunsheet: computed(()=> 
                [layout_types.SHEET_FED_PRESS_MACHINE, 
                layout_types.ROLL_FED_PRESS_MACHINE].
                includes(state.layout.type)),
            svgRect: computed(()=> {
                const rect = state.layout.main? 
                    state.layout.main.bin : null;
                let width = 0;
                let length = 0;
                if (rect){
                    width = rect.width;
                    length = rect.length;
                }
                return {width, length}
            })
        });

        const findLayout = (name) => {
            let layout = null;
            if (state.layouts && state.layouts.length > 0) {
                layout = state.layouts.find(x=> x.name == name)
            }
            return layout;
        }

        const _getSizeLabel = (width, length, uom) => {
            return `${width} x ${length} ${uom}`;
        }

        const getParentRunsheetChildsheetStats = ()=> {
            const parentToRunsheet = state.parentToRunsheet;
            const runsheetToChildsheet = state.runsheetToCutsheet;

            const runsheet = parentToRunsheet.bin;
            const runsheetSize = _getSizeLabel(runsheet.width, 
                runsheet.length, runsheet.uom);
            const runsheetCount = parentToRunsheet.count;

            const childsheet = runsheetToChildsheet.rect;
            const childsheetSize = _getSizeLabel(childsheet.width,
                childsheet.length, childsheet.uom);
            
            const childsheetPerRunsheet = runsheetToChildsheet.count;
            const childsheetCount = runsheetCount * childsheetPerRunsheet;

            const parentUom = runsheet.uom;
            const childUom = childsheet.uom;
            const parentArea = convert(runsheet.width, parentUom).to(childUom) * 
                convert(runsheet.length, parentUom).to(childUom);
            const totalUsedArea = childsheet.width * 
                childsheet.length * childsheetCount;

            const totalUsage = totalUsedArea/parentArea  * 100;
            const totalWasteage =  100 - totalUsage;
            const totalCutCount = parentToRunsheet.cut_count + runsheetToChildsheet.cut_count;

            return {
                layoutType: state.layout.type,
                runsheetSize, runsheetCount, 
                runsheetCountLabel: `${runsheetCount} sheets / material`,
                childsheetSize, childsheetCount,
                childsheetCountLabel: `${childsheetCount} sheets / material`,
                totalUsage, totalWasteage, totalCutCount
            }
        }

        const getRunsheetChildsheetStats = ()=> {
            const runsheetToChildsheet = state.runsheetToCutsheet;

            const runsheet = runsheetToChildsheet.bin;
            const runsheetSize = _getSizeLabel(runsheet.width, 
                runsheet.length, runsheet.uom);
            const runsheetCount = 1;

            const childsheet = runsheetToChildsheet.rect;
            const childsheetSize = _getSizeLabel(childsheet.width,
                childsheet.length, childsheet.uom);
            
            const childsheetPerRunsheet = runsheetToChildsheet.count;
            const childsheetCount = childsheetPerRunsheet;

            const parentUom = runsheet.uom;
            const childUom = childsheet.uom;
            const parentArea = convert(runsheet.width, parentUom).to(childUom) * 
                convert(runsheet.length, parentUom).to(childUom);
            const totalUsedArea = childsheet.width * 
                childsheet.length * childsheetCount;

            const totalUsage = totalUsedArea/parentArea  * 100;
            const totalWasteage =  100 - totalUsage;
            const totalCutCount = runsheetToChildsheet.cut_count;

            return {
                layoutType: state.layout.type,
                runsheetSize, runsheetCount, 
                runsheetCountLabel: `${runsheetCount} sheet or more`,
                childsheetSize, childsheetCount,
                childsheetCountLabel: `${childsheetCount} sheets / runsheet`,
                totalUsage, totalWasteage, totalCutCount
            }
        }

        const getParentChildsheetStats = ()=> {
            const childsheet = state.parentToCutsheet.rect;
            const childsheetSize = `${childsheet.width} x ` +
                `${childsheet.length} ${childsheet.uom}`;
            const childsheetCount = state.parentToCutsheet.count;
            const childUom = childsheet.uom;

            const parentsheet = state.parentToCutsheet.bin;
            const parentUom = parentsheet.uom;
            const parentArea = convert(parentsheet.width, parentUom).to(childUom) * 
                convert(parentsheet.length, parentUom).to(childUom);
            const totalUsedArea = childsheet.width * 
                childsheet.length * childsheetCount;

            const totalUsage = totalUsedArea/parentArea  * 100;
            const totalWasteage =  100 - totalUsage;
            const totalCutCount = state.parentToCutsheet.cut_count;
            
            return {
                layoutType: state.layout.type,
                childsheetSize, childsheetCount,
                childsheetCountLabel: `${childsheetCount} sheets / material`,
                totalUsage, totalWasteage, totalCutCount
            }
        }

        const initializeStats = ()=> {
            let stats = {}; 
            if (state.layouts.length > 0 && state.layout.type) {
                
                if (state.layout.type == layout_types.SHEET_FED_PRESS_MACHINE) {
                    stats = getParentRunsheetChildsheetStats();
                } else if (state.layout.type == layout_types.ROLL_FED_PRESS_MACHINE) {
                    stats = getRunsheetChildsheetStats();
                } else if (state.layout.type == layout_types.DEFAULT) {
                    stats = getParentChildsheetStats();
                }
            }
            emit('load', stats);
        }

        onMounted(initializeStats);
        onUpdated(initializeStats);

        return {
            layout_types, state
        };
    }
}
</script>