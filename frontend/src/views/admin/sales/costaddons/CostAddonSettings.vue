<template>
    <Page title="Admin : Cost Add-ons">
        <hr class="mt-4"/>
        <Tabs>
            <Tab title="Configuration">
                <Section>
                    <ConfigCostAddonList/>
                </Section>
            </Tab>
            <Tab title="Templates">
                <Section>
                    <TemplateCostAddonList/>
                </Section>
            </Tab>
        </Tabs>
    </Page>
</template>
<script>
import Page from '@/components/Page.vue';
import Tabs from '@/components/Tabs.vue';
import Tab from '@/components/Tab.vue';
import Section from '@/components/Section.vue';
import ConfigCostAddonList from '@/views/admin/sales/costaddons/config/ConfigCostAddonList.vue';
import TemplateCostAddonList from '@/views/admin/sales/costaddons/template/TemplateCostAddonList.vue';

export default {
    components: {
        Page, Tabs, Tab, Section, ConfigCostAddonList, TemplateCostAddonList
    }
}
</script>
