<template>
    <div>
        <dt class="text-sm font-bold text-gray-500">{{$props.name}}</dt>
        <dd class="mt-1">
            {{$props.value}}
        </dd>
    </div>
</template>

<script>
export default {
    props: {
        name: String,
        value: String
    }
}
</script>