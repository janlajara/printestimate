<template>
    <div class="md:grid md:grid-cols-2 md:gap-6">
        <ServicesList
            :services="$props.services"/>
        <EstimateDetailSpecificationComponents
            :components="$props.components"/>
    </div>
</template>
<script>
import EstimateDetailSpecificationComponents from './EstimateDetailSpecificationComponents.vue';
import ServicesList from '@/views/pages/sales/commons/ServicesList.vue'; 

export default{
    components: {
        EstimateDetailSpecificationComponents, 
        ServicesList
    },
    props: {
        components: Array,
        services: Array
    }
}
</script>
