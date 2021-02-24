<template>
    <div class="mx-8 py-6 lg:mx-16 md:py-16">
        <h1>{{$props.title}}</h1>
        <slot/>
    </div>
</template>

<script>
export default {
    props: {
        title: String
    }
}
</script>