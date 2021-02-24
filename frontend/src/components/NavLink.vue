<template>
    <div class="flex items-center">
        <Icon :id="$props.icon" class="pr-4 w-8 text-gray-400"
            :class="isSelected? 'text-primary' : ''"/>
        <router-link v-bind="$props" class="w-full" @click="emitSelected"
            :class="isSelected? 'text-primary font-bold' : ''">
            <slot/>
        </router-link>  
    </div>
</template>

<script>
import {computed, watch} from 'vue'
import {useRoute, useRouter, RouterLink} from 'vue-router'
import Icon from '@/components/Icon.vue'

export default {
    props: {
        ...RouterLink.props,
        icon: String,
        selected: String
    },
    emits: ['selected'],
    components: {
        Icon
    },
    setup(props, {emit}){
        const isSelected = computed(()=> props.selected == props.to.name)
        const currentRoute = useRoute()
        const routes = useRouter().getRoutes()
        const linkRoute = routes.filter(
            route => route.name == props.to.name && route.meta.group == null)
        const emitSelected = () => {
            if (linkRoute[0])
                emit('selected', props.to.name)
        }

        watch(()=> currentRoute.name, 
            ()=> {
                if (currentRoute.name == props.to.name)
                    emitSelected()
            }
        )

        return {
            emitSelected,
            isSelected
        }
    }
}
</script>