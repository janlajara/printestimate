<template>
    <teleport to="body">
        <transition name="slide-fade">
            <div class="fixed overflow-y-auto inset-0 bg-gray-900 bg-opacity-30" 
                v-if="$props.isOpen">
                <div class="flex overflow-y-auto items-center justify-center min-h-screen">
                    <div class="bg-white rounded p-9 relative">
                        <span class="material-icons absolute top-3 right-3 
                            text-gray-400 cursor-pointer"
                            @click="$emit('toggle', false)">
                            close</span>
                        <span v-if="$props.heading" class="text-lg font-bold">
                            {{$props.heading}}
                        </span>
                        <div>
                            <span v-if="$props.description">
                                {{$props.description}}
                            </span>
                            <slot/>
                        </div>
                    </div>
                </div>
            </div>
        </transition>
    </teleport>
</template>

<script>
export default {
    props: {
        heading: String,
        description: String,
        isOpen: Boolean
    },
    emits: ['toggle']
}
</script>