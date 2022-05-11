<template>
    <Page title="Admin : Printers">
        <hr class="my-4"/>
        <Tabs :refresh="false">
            <Tab title="Sheet-fed Press">
                <SheetFedPressMachineList/>
            </Tab>
            <Tab title="Roll-fed Press">
                <RollFedPressMachineList/>
            </Tab>
        </Tabs>
    </Page>
</template>

<script>
import Page from '@/components/Page.vue';
import Tabs from '@/components/Tabs.vue';
import Tab from '@/components/Tab.vue';

import SheetFedPressMachineList from './sheetfedpress/SheetFedPressMachineList.vue';
import RollFedPressMachineList from './rollfedpress/RollFedPressMachineList.vue';

export default {
    components: {
        Page, Tabs, Tab, SheetFedPressMachineList, RollFedPressMachineList
    }
}
</script>