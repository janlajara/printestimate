<template>
    <div>
        <Page title="Buttons">
            <Section heading="Regular Buttons"
                description="Here are the samples of regular buttons in various styles."
                class="sm:flex">
                <div class="buttons-group flex flex-grow flex-wrap justify-center my-auto">
                    <Button color="primary">Primary</Button>
                    <Button color="primary">Orange Button</Button>
                    <Button color="secondary">Secondary</Button>
                    <Button color="secondary">White Button</Button>
                </div>
            </Section>
            <Section heading="Buttons with Icon"
                description="Here are the samples of buttons with icon in various styles."
                class="sm:flex">
                <div class="buttons-group flex flex-grow flex-wrap justify-center my-auto">
                    <Button color="primary" icon="restaurant">Kagat!</Button>
                    <Button color="secondary" icon="download">Download</Button>
                    <Button color="secondary" icon="close">Delete</Button>
                </div>
            </Section>
        </Page>
    </div>
</template>

<script>
import Page from '@/components/Page.vue'
import Section from '@/components/Section.vue'
import Button from '@/components/Button.vue'

export default {
    components: {
        Page, Section, Button
    }
}
</script>

<style scoped>
.buttons-group button {
    @apply m-2;
}
</style>
