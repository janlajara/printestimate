<template>
    <article class="py-4"
        :class="$props.heading && $props.headingPosition == 'side' ? 
            'grid md:grid-cols-4 md:gap-4' : ''">
        <div v-if="$props.heading" class="my-2">
            <h2 class="text-lg mb-1 font-semibold">{{$props.heading}}</h2>
            <p v-if="$props.description" class="mb-4">{{$props.description}}</p>
        </div>
        <div :class="$props.heading && $props.headingPosition == 'side' ? 
            'md:col-span-3' : ''">
            <slot/>
        </div>
    </article>
</template>

<script>
export default {
    props: {
        heading: {
            type: String,
            required: false
        },
        headingPosition: {
            type: String,
            default: 'top',
            validator: value =>
                ['side', 'top'].includes(value)
        },
        description: String
    }
}
</script>