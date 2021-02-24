<template>
    <div>
        <Page>
            <div class="md:w-2/3">
                <h1 class="text-2xl sm:text-4xl font-extrabold mb-6">
                    Made with 
                    <span class="text-secondary">Vue 3</span> and 
                    <span class="text-primary">Tailwind CSS</span>
                </h1>
                <p class="mb-6 text-justify">
                    Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. 
                </p>
                <p class="text-justify">
                    Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.
                </p>
            </div>
        </Page>
    </div>
</template>

<script>
import Page from '@/components/Page.vue'

export default {
    components: {
        Page
    }    
}
</script>