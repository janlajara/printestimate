<template>
    <div>
        <Page>
            <div class="md:w-2/3">
                <h1 class="text-2xl sm:text-4xl font-extrabold mb-4">
                    Estimate print jobs 
                    <span class="text-primary">instantly</span>
                </h1>
                <p class="mb-6 text-justify">
                    Printestimate is an app especially designed for printers
                    that follow the <a href="http://budgeted-hourly-cost-rates.com/" 
                        class="text-secondary-dark">budgeted hourly rates (BHRs)</a> 
                    type of costing. 
                </p>
            </div>
            <div>
                <div class="mt-12">
                    <dl class="space-y-10 md:space-y-0 md:grid md:gap-x-8 md:gap-y-10">
                        <div v-for="feature in features" :key="feature.title" class="relative">
                            <dt>
                                <div class="absolute flex items-center justify-center h-12 w-12 
                                    rounded-md bg-primary text-white">
                                    <span class="h-6 w-6 material-icons" aria-hidden="true">
                                        {{feature.icon}}
                                    </span>
                                </div>
                                <p class="ml-16 text-base leading-6 font-medium text-gray-900">
                                    {{feature.title}}</p>
                            </dt>
                            <dd class="mt-1 ml-16 text-sm text-gray-500">
                                {{feature.description}}
                            </dd>
                        </div>
                    </dl>
                </div>
            </div>
        </Page>
    </div>
</template>

<script>
import Page from '@/components/Page.vue'

export default {
    components: {
        Page
    },
    setup(){
        const features = [
            {title: 'Estimates within seconds',
                icon: 'schedule',
                description: 'Quickly create your estimates after a one-time setup.'},
            {title: 'Material costing included',
                icon: 'request_quote',
                description: 'Automatically calculate for the number of raw materials to be consumed.'},
            {title: 'Multiple quantity estimates',
                icon: '123',
                description: 'View estimates for different quantities of the same product all on a single page.'},
        ]
        return {
            features
        }
    }
}
</script>