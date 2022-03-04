<template>
    <div class="md:grid md:grid-cols-2 md:gap-6">
        <EstimateDetailSpecificationServices
            :services="$props.services"/>
        <EstimateDetailSpecificationComponents
            :components="$props.components"/>
    </div>
</template>
<script>
import EstimateDetailSpecificationComponents from './EstimateDetailSpecificationComponents.vue';
import EstimateDetailSpecificationServices from './EstimateDetailSpecificationServices.vue';

export default{
    components: {
        EstimateDetailSpecificationComponents, 
        EstimateDetailSpecificationServices
    },
    props: {
        components: Array,
        services: Array
    }
}
</script>
