<template>
    <div class="grid gap-4 md:grid-cols-2 md:gap-8">
        <Section heading="Export" class="bg-gray-100 p-6 rounded-md"
            description="Download an excel file containing all items in the database.">
            <Button color="secondary" icon="file_download"
                :action="downloadWorkbook">Download</Button>
        </Section>
        <!-- TO BE IMPLEMENTED -->
        <!--Section heading="Import" class="bg-gray-100 p-6 rounded-md"
            description="Upload an excel file to create/update multiple items at once.">
            <Button color="secondary" icon="file_upload"
                :action="()=>{}">Upload</Button>
        </Section-->
    </div>
</template>
<script>
import Section from '@/components/Section.vue';
import Button from '@/components/Button.vue';
import {ItemsWorkbookApi} from '@/utils/apis.js';

import {reactive} from 'vue';

export default {
    components: {
        Section, Button
    },
    setup() {
        const state = reactive({
            download: {
                isLoading: false,
                responseStatus: null
            }
        });
        const downloadWorkbook = async ()=> {
            state.download.isLoading = true;
            const filename = `items-workbook_${new Date().getTime()}.xlsx`;
            const response = await ItemsWorkbookApi.downloadItemsWorkbook(filename);
            state.download.responseStatus = response.status;
            state.download.isLoading = false;
        }

        return {
            state, downloadWorkbook
        }
    },
}
</script>
