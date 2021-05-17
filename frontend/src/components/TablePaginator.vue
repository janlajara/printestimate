<template>
    <div class="grid md:flex">
        <div class="flex-grow mb-4 md:mb-0 md:mr-8">
            <span class="text-xs mr-4">Rows per page:</span>
            <select @input="pagination.changeLimit"
                :value="pagination.limit"
                class="rounded border-none bg-tertiary-light 
                    bg-opacity-50 text-xs">
                <option>5</option>
                <option>10</option>
                <option>50</option>
                <option>100</option>
            </select>
            <span class="my-auto  text-xs ml-8">Total: {{$props.count}} rows</span>
        </div>
        <div class="grid grid-cols-5 gap-4">
            <Button icon="first_page" @click="pagination.first" 
                :disabled="pagination.leftIsDisabled"></Button>
            <Button icon="chevron_left" @click="pagination.back"
                :disabled="pagination.leftIsDisabled"></Button>
            <span class="text-xs my-auto">
                {{pagination.pageNum.current}} / {{pagination.pageNum.max}}</span>
            <Button icon="chevron_right" @click="pagination.forward" 
                :disabled="pagination.rightIsDisabled"></Button>
            <Button icon="last_page" @click="pagination.last"
                :disabled="pagination.rightIsDisabled"></Button>
        </div>
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
            pageNum: computed(()=> {
                let current = 1;
                let max = 1;
                if (props.count && pagination.limit &&
                        props.count > pagination.limit) {
                    current = (pagination.offset / pagination.limit) + 1;
                    max = Math.ceil(props.count / pagination.limit);
                }
                return {current, max};
            }),
            leftIsDisabled: computed(()=> (
                pagination.pageNum.current == 1
            )),
            rightIsDisabled: computed(()=> (
                pagination.pageNum.current == pagination.pageNum.max 
            )),
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
                        props.count % pagination.limit > 0 ?
                            Math.floor(props.count / pagination.limit) * pagination.limit :
                            ((props.count / pagination.limit) - 1) * pagination.limit :
                        0;
                    pagination.offset = offset; 
                    pagination.load();
                }
            },
            load: ()=> {
                emit('change-page',  {limit: pagination.limit, offset: pagination.offset})
            },
            changeLimit: (event)=> {
                pagination.offset = 0;
                emit('change-limit', parseInt(event.target.value));
            }
        });
        watch(()=>props.limit, ()=> {
            if (props.limit != null) {
                pagination.limit = props.limit;
                pagination.load();
            }
        })
        watch(()=>props.count, ()=> {
            if (props.count != null) {
                pagination.offset = 0;
            }
        })
        return {
            pagination
        }
    }
}
</script>