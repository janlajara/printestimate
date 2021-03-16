<template>
    <div>
        <dt class="text-sm font-bold text-gray-500">{{$props.name}}</dt>
        <dd class="mt-1" :class="($props.value == null)? 'text-black text-opacity-30 italic': ''">
            {{($props.value == null)? 'None' : $props.value}}
        </dd>
    </div>
</template>

<script>
export default {
    props: {
        name: String,
        value: {
            type: [Number, String]
        }
    }
}
</script>