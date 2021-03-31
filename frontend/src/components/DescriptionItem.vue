<template>
    <div>
        <dt class="text-sm font-bold text-gray-500">{{$props.name}}</dt>
        <dd class="mt-1 relative" 
            :class="($props.value == null)? 'text-black text-opacity-30 italic': ''">
            <div v-if="$props.loader" :class="loaderWidth"
                class="absolute bg-tertiary-light bg-opacity-50 rounded animate-pulse">
                &nbsp;
            </div>
            <span v-else>{{($props.value == null)? 'None' : $props.value}}</span>
            <span v-if="$props.loader">&nbsp;</span>
        </dd>
    </div>
</template>

<script>
export default {
    props: {
        name: String,
        loader: Boolean,
        value: {
            type: [Number, String],
            required: false
        }
    },
    setup() {
        const widths = ['w-1/2', 'w-1/3', 'w-1/4', 'w-1/5', 'w-2/3', 'w-2/4', 'w-3/4'];
        return {
            loaderWidth: widths[Math.floor(Math.random() * widths.length)]
        }
    }
}
</script>