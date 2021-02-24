<template>
    <button :class="$props.activated? 'bg-secondary-dark bg-opacity-50 rounded' : ''">
        <Icon id="menu" class="w-10" :class="$props.activated? 'text-white': ''"/>
    </button>
</template>
<script>
import Icon from '@/components/Icon.vue'

export default {
    components: {
        Icon
    },
    props: {
        activated: Boolean
    }
}
</script>