<template>
    <nav>
        <slot name="logo"/>
        <span class="mt-6 block"/>
        <NavLink :to="{name: 'home'}"
            icon="home"
            @selected="select" 
            :selected="selected" class="nav-link">
            Home</NavLink>
        <NavMenu
            icon="inventory"
            @selected="select" 
            :selected="selected"
            meta-group="Inventory" class="nav-link">
            Inventory</NavMenu>
        <NavGroup name="Admin">
            <NavLink :to="{name: 'admin-inventory'}"
                icon="inventory"
                @selected="select" 
                :selected="selected" class="nav-link">
                Inventory</NavLink>
            <NavLink :to="{name: 'admin-estimation'}"
                icon="square_foot"
                @selected="select" 
                :selected="selected" class="nav-link">
                Estimation</NavLink>
            <NavMenu
                icon="precision_manufacturing"
                @selected="select" 
                :selected="selected"
                meta-group="Production Admin" class="nav-link">
                Production</NavMenu>
        </NavGroup>
    </nav>
</template>

<script>
import {ref} from 'vue'
import NavGroup from '@/components/NavGroup.vue'
import NavMenu from '@/components/NavMenu.vue'
import NavLink from '@/components/NavLink.vue'

export default {
    components: {
        NavGroup, NavMenu, NavLink
    },
    setup() {
        const selected = ref()
        const select = (value) => {
            selected.value = value
        }
        return {
            selected, select
        }
    }
}
</script>

<style scoped>
@layer components {
    .nav-link {
        @apply pt-1 pb-1;
        @apply mt-2 mb-2;
    }
}
</style>
