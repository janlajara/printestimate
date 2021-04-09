<template>
    <div class="relative">
        <div class="bg-tertiary-light overflow-hidden h-3 flex rounded">
            <div :style="[{width: ($props.percent && $props.percent > 0 ? $props.percent : 3) + '%'}]" 
                class="flex flex-col text-center whitespace-nowrap text-white justify-center"
                :class="style.color">
            </div>
            <slot/>
        </div>
    </div>
</template>

<script>
import {reactive, computed} from 'vue'

export default {
    props: {
        color: {
            type: String,
            validator: (value) => 
                ['primary', 'secondary', 'tertiary', 'variable',
                 'gray', 'red', 'yellow', 'green',
                 'blue', 'indigo', 'purple', 'pink']
                .indexOf(value) !== -1
        },
        percent: Number
    },
    setup(props) {
        const style = reactive({
            color: computed(()=> {
                if (props.color == 'variable' && props.percent != null) {
                    let clr = 'red'
                    if (props.percent >= 75) clr = 'green';
                    else if (props.percent >= 25) clr = 'yellow';
                    return `bg-${clr}-500`; 
                } else if (props.color) {
                    return `bg-${props.color}-500`; 
                } else {
                    return 'bg-secondary';
                }
            })
        })
        return {
            style
        }
    }
}
</script>