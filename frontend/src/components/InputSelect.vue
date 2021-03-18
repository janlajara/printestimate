<template>
    <div class="input">
        <label class="input-label">{{$props.name}}
          <span v-if="$props.required" class="text-secondary-light">*</span>
          <span v-if="$props.disabled" 
                class="material-icons text-sm text-secondary-light">lock</span>
        </label>
        <div class="rounded-md shadow-sm" v-click-outside="()=>toggleDropdown(false)">
            <div class="relative">
              <input type="text" class="rounded input-field cursor-pointer"
                :class="($props.disabled)? 'text-gray-400' : ''"
                :value="selectedJoined" :disabled="$props.disabled"
                @click="toggleDropdown(!state.isDroppedDown)" readonly/>
              <span class="absolute material-icons right-0 m-1 transform"
                :class="state.isDroppedDown? 'rotate-180' : ''">
                arrow_drop_down</span>
              <div v-show="state.isDroppedDown" 
                class="shadow-md rounded bg-white absolute w-full mt-1 z-10">
                <div v-for="option in state.options" :key="option.value"
                  class="p-2 hover:bg-secondary-light hover:bg-opacity-20 text-sm cursor-pointer"
                  @click="select(option)">
                  <input v-if="$props.multiple" type="checkbox" 
                    class="input-checkbox mr-4" disabled 
                    :name="name" :checked="option.isSelected"/> 
                    <span :class="(option.value == null)? 'text-gray-400 italic' : ''">
                      {{(option.value == null)?  'None': option.label}}</span>
                </div>
              </div>
            </div>
        </div>
    </div>
</template>

<script>
import {reactive, computed, watch} from 'vue'

export default {
    props: {
        name: String,
        multiple: Boolean,
        required: Boolean,
        disabled: Boolean,
        options: {
            type: Array 
            //Array of Objects 
            //{label:String, value:number, isSelected:Boolean}
        },
    },
    setup(props, {emit}) {  
      const state = reactive({
        baseOptions: props.options.filter(prop => prop.value != null),
        options: computed(()=> {
          const options = (!props.required && !props.multiple)? 
            [{value: null, label: ''}].concat(state.baseOptions):
            state.baseOptions;
          return options;
        }),
        isDroppedDown: false,
      }); 
      watch(()=>props.options, ()=> {
        state.baseOptions = props.options.filter(prop => prop.value != null);
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
        const val = (props.multiple)? selectedIds : selectedIds.shift(); 
        if (emit) emit('input', val);
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