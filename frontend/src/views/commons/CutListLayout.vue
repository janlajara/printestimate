<template>
    <div class="mt-2 bg-gray-200 px-4 py-4 rounded-md">
        <Svg :svg-height="250" v-if="state.parentToRunsheet != null"
            :view-box-width="state.parentToRunsheet.bin.width" 
            :view-box-height="state.parentToRunsheet.bin.length">
            <Rectangle 
                :width="state.parentToRunsheet.bin.width"
                :height="state.parentToRunsheet.bin.length"
                stroke="grey" :stroke-width="1" fill="white"/>
            <ParentSheetShape :key="key"
                v-for="(layout, key) in state.parentToRunsheet.layouts"
                :view-box-width="state.parentToRunsheet.bin.width"
                :view-box-length="state.parentToRunsheet.bin.length"
                :width="layout.width"
                :length="layout.length"
                stroke="#6dd297"
                fill="#c2ffdb"
                :padding-top="0"
                :padding-right="0"
                :padding-bottom="0"
                :padding-left="0">
            </ParentSheetShape>
        </Svg>
    </div>
</template>
<script>
import Svg from '@/utils/svg/Svg.vue';
import Rectangle from '@/utils/svg/Rectangle.vue';
import ParentSheetShape from '@/views/admin/production/machines/sheetfedpress/parentsheets/ParentSheetShape.vue';
//import ChildSheetShape from '@/views/admin/production/machines/sheetfedpress/childsheets/ChildSheetShape.vue';

import {reactive, computed} from 'vue';

export default {
    props: {
        layouts: {
            type: Array,
            default: ()=> []
        }
    },
    components: {
        Svg, Rectangle, ParentSheetShape,// ChildSheetShape
    },
    setup(props) {
        const state = reactive({
            parentToRunsheet: computed(()=> 
                props.layouts.find(x=> x.name == 'Parent-to-runsheet') 
            ),
            runsheetToCutsheet: computed(()=> 
                props.layouts.find(x=> x.name == 'Runsheet-to-cutsheet')
            ),
            cutsheetToTrimsheet: computed(()=> 
                props.layouts.find(x=> x.name == 'Cutsheet-to-trimsheet')
            )
        });

        return {
            state
        };
    }
}
</script>