<template>
    <Svg :svg-height="250" v-if="state.parentToRunsheet == true"
        :view-box-width="state.parentToRunsheet.bin.width" 
        :view-box-height="state.parentToRunsheet.bin.length">
        <Rectangle 
            :width="state.parentToRunsheet.bin.width"
            :height="state.parentToRunsheet.bin.length"
            :stroke-width="1"
            fill="white"/>
    </Svg>
</template>
<script>
import Svg from '@/utils/svg/Svg.vue';
import Rectangle from '@/utils/svg/Rectangle.vue';

import {reactive, computed} from 'vue';

export default {
    props: {
        layouts: {
            type: Array,
            default: ()=> []
        }
    },
    components: {
        Svg, Rectangle
    },
    setup(props) {
        const state = reactive({
            parentToRunsheet: computed(()=> 
                props.layouts.find(x=> x.name == 'Parent-to-runsheet') || []
            ),
            runsheetToCutsheet: computed(()=> 
                props.layouts.find(x=> x.name == 'Runsheet-to-cutsheet') || []
            ),
            cutsheetToTrimsheet: computed(()=> 
                props.layouts.find(x=> x.name == 'Cutsheet-to-trimsheet') || []
            )
        });

        return {
            state
        };
    }
}
</script>