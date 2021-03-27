<template>
    <div class="flex">
        <div>
            <span class="text-xs mr-4">Rows per page:</span>
            <select @input="pagination.changeLimit"
                :value="pagination.limit"
                class="rounded-md shadow-sm border-none bg-tertiary-light 
                    bg-opacity-50 text-xs mr-8">
                <option>5</option>
                <option>10</option>
                <option>50</option>
                <option>100</option>
            </select>
        </div>
        <Button icon="first_page" @click="pagination.first" class="mr-4"></Button>
        <Button icon="chevron_left" @click="pagination.back" class="mr-4"></Button>
        <span class="text-xs my-auto mr-4">{{pagination.pageLabel}}</span>
        <Button icon="chevron_right" @click="pagination.forward" class="mr-4"></Button>
        <Button icon="last_page" @click="pagination.last"></Button>
    </div>
</template>

<script>
import Button from '@/components/Button.vue'
import {reactive, watch, computed} from 'vue';

export default {
    components: {
        Button
    },
    props: {
        limit: Number,
        count: Number
    },
    emits: ['change-limit', 'change-page'],
    setup(props, {emit}) {
        const pagination = reactive({
            limit: 5,
            offset: 0,
            pageLabel: computed(()=> {
                let current = 1;
                let max = 1;
                if (props.count && pagination.limit &&
                        props.count > pagination.limit) {
                    current = (pagination.offset / pagination.limit) + 1;
                    max = parseInt(props.count / pagination.limit) + 1;
                }
                return `${current} /  ${max}`;
            }),
            first: ()=> {
                pagination.offset = 0;
                pagination.load();
            },
            back: ()=> {
                if (pagination.offset >= pagination.limit) {
                    pagination.offset -= pagination.limit;
                    pagination.load();
                }
            },
            forward: ()=> {
                if (pagination.offset + pagination.limit <  props.count) {
                    pagination.offset += pagination.limit;
                    pagination.load();
                }
            },
            last: ()=> {
                if (props.count && pagination.limit) {
                    const offset = props.count > pagination.limit?
                        parseInt(props.count / pagination.limit) * pagination.limit :
                        0;
                    pagination.offset = offset; 
                    pagination.load();
                }
            },
            load: ()=> {
                emit('change-page',  {limit: pagination.limit, offset: pagination.offset})
            },
            changeLimit: (event)=> {
                emit('change-limit', parseInt(event.target.value));
                pagination.first();
            }
        });
        watch(()=> props.limit, ()=> {
            if (props.limit != null) {
                pagination.limit = props.limit;
                pagination.load();
            }
        })
        return {
            pagination
        }
    }
}
</script>