<template>
    <Section heading="Services">
        <div class="bg-gray-100 w-full rounded-md p-4 relative my-4">
            <div class="flow-root">
                <ul role="list">
                    <li v-for="(service, key) in state.data.services" :key="key" class="relative">
                        <div class="pb-4">
                            <span v-if="key !== state.data.services.length - 1" class="absolute top-3 left-3 -ml-px h-full w-0.5 bg-gray-200" aria-hidden="true" />
                            <div class="relative flex space-x-3">
                                <div>
                                    <span class="h-6 w-6 rounded-full flex items-center justify-center bg-secondary-light">
                                        <span class="material-icons text-sm transition"
                                            :class="service.isExpanded ? 'transform rotate-90' : ''">
                                            chevron_right
                                        </span>
                                    </span>
                                </div>
                                <div class="min-w-0 my-0.5 cursor-pointer"
                                    @click="()=>service.toggle(key)">
                                    <div class="flex">
                                        <p class="text-sm text-gray-500">
                                            <span class="font-medium text-gray-900">{{ service.name }}</span>
                                        </p>
                                    </div>
                                    <div 
                                        class="text-xs whitespace-nowrap text-gray-500">
                                        <transition 
                                            enter-active-class="transition ease-out duration-100" 
                                            enter-from-class="transform origin-top opacity-0 scale-y-75" 
                                            enter-to-class="transform origin-top opacity-100 scale-100" 
                                            leave-active-class="transition ease-in duration-75" 
                                            leave-from-class="transform origin-top opacity-100 scale-100" 
                                            leave-to-class="transform origin-top opacity-0 scale-y-75">
                                            <div v-show="service.isExpanded">
                                                <ul v-for="(operation, i) in service.operations.filter(o => o.activities.length > 0)" 
                                                        :key="i" class="list-disc pl-3 pb-2">
                                                    <li class="font-bold">{{[operation.name, operation.material].join(' ')}}</li>
                                                    <ul class="pl-4">
                                                        <li v-for="(activity, j) in operation.activities" :key="j">
                                                            - {{activity.name}} {{activity.notes}}
                                                        </li>
                                                    </ul>
                                                </ul>
                                            </div>
                                        </transition>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </li>
                </ul>
            </div>
            <div v-show="state.data.services.length > 0"
                class="px-4 absolute top-4 right-0 cursor-pointer" 
                    @click="state.data.expandAll.toggle">
                <span class="material-icons bg-gray-300 rounded-full p-1">
                    {{state.data.expandAll.isAllExpanded? 'unfold_less' : 'unfold_more'}}
                </span>
            </div>
        </div>
    </Section>
</template>
<script>
import Section from '@/components/Section.vue';

import {reactive, computed, onBeforeMount, onUpdated} from 'vue';

export default {
    components: {
        Section
    },
    props: {
        services: {
            type: Array,
            default: ()=>[]
        }
    },
    setup(props) {
        const state = reactive({
            isProcessing: false,
            data: {
                expandAll: {
                  isAllExpanded: computed(()=> 
                    state.data.services.filter(x=> !x.isExpanded) == 0),
                  toggle: ()=>{
                      const isAllExpanded = state.data.expandAll.isAllExpanded;
                      state.data.services
                        .filter(x=> x.isExpanded == isAllExpanded)
                        .forEach(x=> {
                            x.isExpanded = !x.isExpanded;
                      });
                  }  
                },
                services: []
            },
        });

        const initialize = ()=> {
            let services = [...props.services];
            if (services && services.length > 0) {
                state.data.services = services
                    .filter(s => s.operations.find(o => o.activities.length > 0))
                    .map(x=> ({
                        ...x,
                        isExpanded: false,
                        toggle: (index)=> {
                            if (index != null && index <= state.data.services.length) {
                                const service = state.data.services[index];
                                service.isExpanded = !service.isExpanded;}
                            }
                }));
            }
        }

        onBeforeMount(initialize);
        onUpdated(initialize);

        return {
            state
        }
    }
}
</script>
