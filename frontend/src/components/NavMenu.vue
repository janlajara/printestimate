<template>
    <div> 
        <div @click.prevent="$emit('selected', $props.metaGroup)"
            class="flex items-center cursor-pointer">
            <Icon :id="$props.icon" class="pr-4 w-8" 
                :class="collapsed? 'text-primary' : 'text-gray-400'"/>
            <a href="#" class="flex-grow" 
                :class="collapsed? 'text-primary font-bold' : ''">
                <slot/>
            </a>
            <Icon id="expand_more" class="transform text-gray-400" 
                :class="collapsed? '' : 'rotate-90'"/>
        </div>
        <div ref="navLinks"
            class="flex flex-col overflow-hidden transition-height duration-100 ease-out"
            :style="height? {height: `${collapsed? height:0}px`}: {}" >
            <NavLink :to="{name: route.name}" v-for="(route, i) in group" :key="i"
                class="pt-3 text-sm" :class="$route.name == route.name? 'text-primary' : ''">
                {{route.meta.label}}
            </NavLink>
        </div>
    </div>
</template>

<script>
import {ref, onMounted, computed, watch, onBeforeMount} from 'vue'
import {useRoute, useRouter} from 'vue-router'
import NavLink from '@/components/NavLink.vue'
import Icon from '@/components/Icon.vue'

export default {
    props: {
        selected: String,
        metaGroup: String,
        icon: String
    },
    emits: ['selected'],
    components: {
        NavLink, Icon
    },
    setup(props, {emit}) {
        const route = useRoute()
        const routes = useRouter().getRoutes()
        const navLinks = ref()
        const height = ref()
        const collapsed = computed(()=> props.selected == props.metaGroup)
        const emitSelected = ()=> {
            if (route.meta.group == props.metaGroup) {
                emit('selected', props.metaGroup)
            }
        }

        watch(()=>route.name, emitSelected)
        onBeforeMount(emitSelected)
        onMounted(()=> {
            height.value = navLinks.value.clientHeight;
        })

        let group = []
        if (props.metaGroup) 
            group = routes.filter( r => {return props.metaGroup == r.meta.group})

        return {
            group,
            collapsed,
            navLinks,
            height
        }
    }
}
</script>
