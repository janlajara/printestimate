<template>
    <Page title="Admin : Machines">
        <hr class="my-4"/>
        <Tabs>
            <Tab title="Sheet-fed Press">
                <SheetFedPressMachineList/>
            </Tab>
            <Tab title="Roll-fed Press">
            </Tab>
            <Tab title="Cutter">
            </Tab>
        </Tabs>
    </Page>
</template>

<script>
import Page from '@/components/Page.vue';
import Tabs from '@/components/Tabs.vue';
import Tab from '@/components/Tab.vue';

import SheetFedPressMachineList from '@/views/admin/production/machines/sheetfedpress/SheetFedPressMachineList.vue';

export default {
    components: {
        Page, Tabs, Tab, SheetFedPressMachineList
    }
}
</script>