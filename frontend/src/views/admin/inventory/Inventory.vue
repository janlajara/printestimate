<template>
    <Page title="Admin : Inventory">
        <Tabs>
            <Tab title="Item">
                <Section heading="General Content" description="General tab content goes here.">
                    
                </Section>
            </Tab>
            <Tab title="Unit of Measure">
                <UnitOfMeasure/>
            </Tab>
        </Tabs>
    </Page>
</template>

<script>
import Page from '@/components/Page.vue';
import Tabs from '@/components/Tabs.vue';
import Tab from '@/components/Tab.vue';
import UnitOfMeasure from '@/views/admin/inventory/UnitOfMeasure.vue';

export default {
    components: {
        Page, Tabs, Tab, UnitOfMeasure
    }
}
</script>