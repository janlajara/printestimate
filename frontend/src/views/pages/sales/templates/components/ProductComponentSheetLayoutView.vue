<template>
    <div class="mt-4 grid w-full">
        <div class="flex justify-end">
            <Button icon="dashboard" color="none" :action="state.hideToggle">
                {{state.isHidden? 'Show': 'Hide' }} Layout</Button>
        </div>
        <div :class="[state.isHidden? 'hidden' : '', '']">
            <CutListLayout/>
        </div>
    </div>
</template>

<script>
import Button from '@/components/Button.vue';
import CutListLayout from '@/views/commons/CutListLayout.vue';

import {reactive} from 'vue';

export default {
    components: {
        Button, CutListLayout
    },
    setup() {
        const state = reactive({
            isHidden: true,
            hideToggle: ()=> {
                state.isHidden = !state.isHidden;
            }
        });

        return {
            state
        }
    }
}
</script>