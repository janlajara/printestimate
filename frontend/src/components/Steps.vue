<template>
    <Section class="flex">
        <div class="flex-shrink flex flex-col space-y-4">
            <div v-for="(step, index) in state.steps" :key="index"
                @click="()=>state.select(index)"
                class="border-l-4 py-2 pl-4 pr-6 cursor-pointer"
                :class="state.currentStep >= index ? 
                    'border-secondary' : ''">
                <p class="text-xs uppercase text-secondary">
                    Step {{index+1}}</p>
                <p class="my-auto text-sm font-bold"
                    :class="state.selectedStep == index ? 'text-secondary' : 
                        state.currentStep < index ? 'text-gray-400' : ''">
                    {{step.props.name}}</p>
            </div>
        </div>
        <div class="flex flex-grow">
            <div class="w-full">
                <slot/>
            </div>
        </div>
    </Section>
</template>

<script>
import Section from '@/components/Section.vue';
import {reactive, onBeforeMount, provide} from 'vue';

export default {
    components: {
        Section
    },
    props: {
        type: String
    },
    setup(props, {slots}) {
        console.log(props);
        const state = reactive({
            currentStep: 0,
            selectedStep: 0,
            steps: [],
            count: 0,
            select: (index)=> {
                //if (state.currentStep >= index)
                    state.selectedStep = index;
            }
        });
        /*const selectStep = (index) => {
            state.currentStep = index
        };*/
        provide('StepsManager', state);

        onBeforeMount(()=> {
            if (slots.default) {
                state.steps = slots.default().filter( child => {
                    return child.type.name==='Step'})
                console.log(state.steps);
            }
        });

        return {
            state
        }
    }
}
</script>