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
        <NavMenu
            icon="request_quote"
            @selected="select" 
            :selected="selected"
            meta-group="Sales" class="nav-link">
            Sales</NavMenu>
        <NavGroup name="Admin">
            <NavMenu
                icon="precision_manufacturing"
                @selected="select" 
                :selected="selected"
                meta-group="Production Admin" class="nav-link">
                Production</NavMenu>
            <NavMenu
                icon="request_quote"
                @selected="select" 
                :selected="selected"
                meta-group="Sales Admin" class="nav-link">
                Sales</NavMenu>
            <NavLink :to="{name: 'admin-inventory'}"
                icon="inventory"
                @selected="select" 
                :selected="selected" class="nav-link">
                Inventory</NavLink>
            <NavMenu
                icon="miscellaneous_services"
                @selected="select" 
                :selected="selected"
                meta-group="Miscellaneous" class="nav-link">
                Miscellaneous</NavMenu>
        </NavGroup>
        <NavGroup name="References">
            <NavLink :to="{name: 'references-userguide'}"
                icon="local_library"
                @selected="select" 
                :selected="selected" class="nav-link">
                User Guide</NavLink>
            <NavLink :to="{name: 'references-documentation'}"
                icon="description"
                @selected="select" 
                :selected="selected" class="nav-link">
                Documentation</NavLink>
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
