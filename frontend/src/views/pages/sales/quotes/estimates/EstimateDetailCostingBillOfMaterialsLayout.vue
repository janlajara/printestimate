<template>
    <div class="border-t-2 border-dotted text-gray-500 grid grid-cols-2 py-1">
        <div class="text-sm">
            <div class="ml-8 my-auto">Layout</div>
            <div class="ml-12 grid">
                <span>Runsheet size:</span>
                <span>Runsheets per material:</span>
                <span>Finalsheets per material:</span>
                <span class="pt-3">Usage:</span>
                <span>Wastage:</span>
                <span class="pt-3">Raw-to-running cut:</span>
                <span >Running-to-final cut:</span>
            </div>
        </div>
        <div>
            <CutListLayout 
                :layouts="state.data.layouts"
                :svg-height="140"/>
        </div>
    </div>
</template>
<script>
import CutListLayout from '@/views/commons/sheetfedpress/CutListLayout.vue';
import {reactive, computed} from 'vue';

export default {
    components: {
        CutListLayout
    },
    props: {
        layouts: Array
    },
    setup(props) {
        const state = reactive({
            data: {
                layouts: computed(()=>props.layouts),
                meta: computed(()=>{
                    let stats = {
                        count:0, usage: 0, wastage: 0, cutCount: 0}
                    if (props.layouts) {
                        stats = props.layouts.map(x=>({
                            count: x.count,
                            usage: x.usage,
                            wastage: x.wastage,
                            cutCount: x.cut_count
                        }));
                    }
                    return stats;
                })
            }
        });
        return {
            state
        }
    },
}
</script>
