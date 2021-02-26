<template>
    <Page title="Admin : Inventory">
        <Tabs>
            <Tab title="Item">
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