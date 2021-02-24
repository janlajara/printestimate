<template>
    <div class="flex">
        <span class="material-icons text-base m-auto">{{$props.id}}</span>
    </div>
</template>

<script>

export default {
    props: {
        id: String
    }
}
</script>