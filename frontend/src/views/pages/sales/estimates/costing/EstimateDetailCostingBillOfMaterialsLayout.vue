<template>
    <div v-if="$props.layouts && $props.layouts.length > 0"
        class="border-t-2 border-dotted text-gray-500 grid grid-cols-2 py-1">
        <div class="text-sm">
            <div class="ml-8 my-auto">Layout</div>
            <div v-if="state.data.stats" 
                class="ml-12 grid">
                <dl v-if="state.data.stats.hasRunsheet"
                    class="grid grid-cols-2 my-4">
                    <dt>Runsheet size:</dt>
                    <dd>{{state.data.stats.runsheetSize}}</dd>

                    <dt>Runsheet count:</dt>
                    <dd>
                        {{formatQuantity(state.data.stats.runsheetPerParent, 'out', 'outs')}}
                        / whole sheet
                    </dd>

                    <dt>Finalsheet count:</dt>
                    <dd>
                        {{formatQuantity(state.data.stats.childsheetCount, 'out', 'outs')}}
                        / whole sheet
                    </dd>

                    <dt>Usage:</dt>
                    <dd>{{formatNumber(state.data.stats.totalUsage, 2)}}%</dd>

                    <dt>Wastage:</dt>
                    <dd>{{formatNumber(state.data.stats.totalWasteage, 2)}}%</dd>

                    <dt>Total # of cuts:</dt>
                    <dd>{{state.data.stats.totalCutCount}}</dd>
                </dl>
                <dl v-else class="grid grid-cols-2 my-4">
                    <dt>Finalsheet count:</dt>
                    <dd>
                        {{formatQuantity(state.data.stats.childsheetCount, 'out', 'outs')}}
                        / whole sheet
                    </dd>

                    <dt>Usage:</dt>
                    <dd>{{formatNumber(state.data.stats.totalUsage, 2)}}%</dd>

                    <dt>Wastage:</dt>
                    <dd>{{formatNumber(state.data.stats.totalWasteage, 2)}}%</dd>

                    <dt>Total # of cuts:</dt>
                    <dd>{{state.data.stats.totalCutCount}}</dd>
                </dl>
            </div>
        </div>
        <div>
            <CutListLayout 
                @load="value => state.data.stats = value"
                :layout-type="$props.machineType"
                :layouts="$props.layouts"
                :svg-height="140"/>
        </div>
    </div>
</template>
<script>
import CutListLayout from '@/views/commons/layout/CutListLayout.vue';
import {reactive} from 'vue';
import {formatNumber, formatQuantity} from '@/utils/format.js';

export default {
    components: {
        CutListLayout
    },
    props: {
        machineType: String,
        layouts: Array
    },
    setup() {
        const state = reactive({
            data: {
                stats: null
            }
        });
        return {
            state, formatNumber, formatQuantity
        }
    },
}
</script>
