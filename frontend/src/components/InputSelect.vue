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
                :value="selectedValue" :disabled="$props.disabled" 
                :readonly="!$props.customizable"
                @blur="inputCustomValue"
                @click="toggleDropdown(!state.isDroppedDown)"/>
              <span class="absolute material-icons right-0 m-1 transform"
                :class="state.isDroppedDown? 'rotate-180' : ''">
                arrow_drop_down</span>
              <div v-show="state.isDroppedDown" 
                class="shadow-md rounded bg-white absolute w-full 
                mt-1 z-10 max-h-60 overflow-auto">
                <div v-for="option in state.options" :key="option.value"
                  class="p-2 hover:bg-secondary-light hover:bg-opacity-20 
                  text-sm cursor-pointer"
                  @click="select(option)">
                  <div class="flex w-full">
                    <input v-if="$props.multiple" type="checkbox" 
                      class="input-checkbox mr-4 my-auto" disabled 
                      :name="name" :checked="option.isSelected"/> 
                    <div class="flex justify-between w-full align-middle">
                      <span :class="(option.value == null)? 'text-gray-400 italic' : ''">
                        {{(option.value == null)?  
                            'None': option.label ? 
                              option.label : [option.value, $props.postfix].join(' ')}}</span>
                      <span v-if="option.description" class="text-gray-400">
                        {{option.description}}
                      </span>
                    </div>
                  </div>
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
        postfix: String,
        multiple: Boolean,
        required: Boolean,
        disabled: Boolean,
        customizable: Boolean,
        regex: Object,
        options: {
            type: Array 
            //Array of Objects 
            //{label:String, value:number, description:String, isSelected:Boolean}
        },
    },
    emits: ['input'],
    setup(props, {emit}) {  
      const state = reactive({
        baseOptions: props.options.filter(prop => prop && prop.value != null),
        options: computed(()=> {
          const options = (!props.required && !props.multiple)? 
            [{value: null, label: ''}].concat(state.baseOptions):
            state.baseOptions;
          return options;
        }),
        isDroppedDown: false,
        customInput: null,
      }); 

      watch(()=>props.options, ()=> {
        state.baseOptions = props.options.filter(prop => prop && prop.value != null);
      });

      const selectedOptions = computed(() => {
        let selected = state.options.filter(option=> option.isSelected);
        if (!props.multiple && selected.length > 1) selected.splice(0,1);
        return selected;
      });

      const selectedValue = computed(() => {
        let selectedValue = selectedOptions.value
          .map(option=> option.label? 
            option.label : 
            [option.value, props.postfix].join(' '))
          .join(", ");
        
        if (props.customizable && state.customInput)
          selectedValue = [state.customInput, props.postfix].join(' ');
        return selectedValue;
      });

      const toggleDropdown = (value) => {
        state.isDroppedDown = value;
      };

      const inputCustomValue = (event) => {
        let input = event.target.value;
        if (props.regex != null) {
          const matchFound = input.match(props.regex);
          if (matchFound) input = matchFound[0];
        }
        state.customInput = input;
        emit('input', input);
      }

      const select = (option) => { 
        if (props.multiple) {
          option.isSelected = !option.isSelected
        } else {
          state.options.forEach(o => {
            const match_found = option.value == o.value;
            o.isSelected = (match_found)? true : false;
          });
          toggleDropdown(false);
        }
        const selectedIds = selectedOptions.value.map(o=> o.value);
        const val = (props.multiple)? selectedIds : selectedIds.shift(); 
        emit('input', val);
      };

      return {
        state, toggleDropdown, select, selectedValue, inputCustomValue
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