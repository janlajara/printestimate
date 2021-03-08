<template>
    <Page title="Tabs">
        <Tabs>
            <Tab title="General">
                <Section heading="General Content" description="General tab content goes here.">
                    <p class="text-justify">Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>
                </Section>
            </Tab>
            <Tab title="Advanced">
                <Section heading="Advanced Content" description="Advanced tab content goes here.">
                    <p class="text-justify">Sed ut perspiciatis unde omnis iste natus error sit voluptatem accusantium doloremque laudantium, totam rem aperiam, eaque ipsa quae ab illo inventore veritatis et quasi architecto beatae vitae dicta sunt explicabo.</p>
                </Section>
            </Tab>
            <Tab title="Miscellaneous">
                <Section heading="Miscellaneous Content" description="Miscellaneous tab content goes here.">
                    <p class="text-justify">Nemo enim ipsam voluptatem quia voluptas sit aspernatur aut odit aut fugit, sed quia consequuntur magni dolores eos qui ratione voluptatem sequi nesciunt. Neque porro quisquam est, qui dolorem ipsum quia dolor sit amet, consectetur, adipisci velit, sed quia non numquam eius modi tempora incidunt ut labore et dolore magnam aliquam quaerat voluptatem.</p>
                </Section>
            </Tab>
        </Tabs>
    </Page>
</template>

<script>
import Page from '@/components/Page.vue'
import Tabs from '@/components/Tabs.vue'
import Tab from '@/components/Tab.vue'
import Section from '@/components/Section.vue'

export default {
    components: {
        Page, Tabs, Tab, Section
    }
}
</script>