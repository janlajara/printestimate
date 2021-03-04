<template>
    <div class="input">
        <label class="input-label">{{$props.name}}</label>
        <div class="rounded-md shadow-sm" v-click-outside="()=>toggleDropdown(false)">
            <div class="relative">
              <input type="text" class="rounded input-field cursor-pointer"
                :value="selectedJoined"
                @click="toggleDropdown(!state.isDroppedDown)" readonly/>
              <span class="absolute material-icons right-0 m-1 transform"
                :class="state.isDroppedDown? 'rotate-180' : ''">
                arrow_drop_down</span>
              <div v-show="state.isDroppedDown" class="shadow-md rounded bg-white absolute w-full mt-1">
                <div v-for="option in state.options" :key="option.value"
                  class="p-2 hover:bg-secondary-light hover:bg-opacity-20 text-sm cursor-pointer"
                  @click="select(option)">
                  <input v-if="$props.multiple" type="checkbox" 
                    class="input-checkbox mr-4" disabled 
                    :name="name" :checked="option.isSelected"/> 
                  {{option.label}}
                </div>
              </div>
            </div>
            <!--select v-else class="rounded input-field">
                <option disabled value="">Select</option>
                <option v-for="option in $props.options" :key="option.value">
                    {{option.label}}
                </option>
            </select-->
        </div>
    </div>
</template>

<script>
import {reactive, computed} from 'vue'

export default {
    props: {
        name: String,
        multiple: Boolean,
        options: {
            type: Array 
            //Array of Objects 
            //{label:String, value:number, isSelected:Boolean}
        }
    },
    setup(props, {emit}) {  
      const state = reactive({
        options: props.options,
        isDroppedDown: false,
      }); 
      const selectedOptions = computed(() => 
        state.options
          .filter(option=> option.isSelected)
      );
      const selectedJoined = computed(() => 
        selectedOptions.value
          .map(option=> option.label)
          .join(", ")
      );
      const toggleDropdown = (value) => {
        state.isDroppedDown = value;
      };
      const select = (option) => { 
        if (props.multiple) {
          option.isSelected = !option.isSelected
        } else {
          state.options.forEach(o => {
            o.isSelected = (option.value == o.value)? true : false;
          });
          toggleDropdown(false);
        }
        const selectedIds = selectedOptions.value.map(o=> o.value);
        if (emit) emit('input', selectedIds);
      };
      return {
        state, toggleDropdown, select, selectedJoined
      };
    }
}
</script>

<style scoped>
@layer components {
  .input {
    @apply mt-2;
  }

  .input-label {
    @apply text-sm font-medium;
  }

  .input-field {
    @apply w-full border-none bg-gray-200 text-sm;
  }

  .input-checkbox {
    @apply border-none rounded bg-gray-300 text-primary;
  }

  .input-checkbox:checked {
    @apply bg-checkbox;
  }
}
</style>