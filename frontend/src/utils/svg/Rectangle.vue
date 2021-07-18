<template>
    <div>
        <svg :id="`rect-${state.id}`"></svg>
    </div>
</template>
<script>
import Snap from 'snapsvg-cjs';
import {v4 as uuid} from 'uuid';
import {reactive, onMounted} from 'vue';

export default {
    setup(){
        const state = reactive({
            id: uuid()
        });
        console.log(state.id);

        onMounted(()=> {
            const elementId = `#rect-${state.id}`;
            const snap = Snap(elementId);

            if (snap) {
                const circle = snap.circle(150, 150, 100);
                circle.attr({
                    fill: "#bada55",
                    stroke: "#000",
                    strokeWidth: 5
                });
            }
        })

        return {
            state
        }
    }
}
</script>