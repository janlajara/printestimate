<template>
    <div>
        <Page title="Forms">
            <p>Here are some sample layout for fields.</p>
            <br/><hr/>
            <Section heading="Some Fields">
                <div class="grid grid-cols-1 lg:grid-cols-2 inputs">
                    <InputText name="Username" type="text" placeholder="abcd1234"/>
                    <InputText name="Price" type="number" prefix="PHP"/>
                    <InputText name="Quantity" type="number" postfix="pieces"/>
                    <InputText name="Website" type="text" prefix="www." postfix=".com"/>
                    <InputTextarea name="Description"/>
                </div>
            </Section>
            <Section heading="Others">
                <InputSelect name="City" class="md:w-1/3"
                    :options="[
                        {label: 'Manila', value: 'MNL'},
                        {label: 'Calamba', value: 'CLB'},
                        {label: 'Lumban', value: 'LMB'}]"/>
                <FieldSet name="Gender">
                    <div class="flex">
                        <InputRadio name="Gender" option="Male" />
                        <InputRadio name="Gender" option="Female"/>
                        <InputRadio name="Gender" option="Others"/>
                    </div>
                </FieldSet>
            </Section>
            <hr/>
            <Section heading="Terms and Conditions">
                <InputCheckbox name="Read" option="read" label="I have read the everything."/>
                <InputCheckbox name="Terms" option="agree" label="I agree to the terms and conditions.">
                    Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. 
                </InputCheckbox>
            </Section>
        </Page>
    </div>
</template>

<script>
import Page from '@/components/Page.vue'
import Section from '@/components/Section.vue'
import InputText from '@/components/InputText.vue'
import InputTextarea from '@/components/InputTextarea.vue'
import InputSelect from '@/components/InputSelect.vue'
import InputRadio from '@/components/InputRadio.vue'
import InputCheckbox from '@/components/InputCheckbox.vue'
import FieldSet from '@/components/FieldSet.vue'

export default {
    components: {
        Page, Section, InputText, InputTextarea, InputSelect,
        InputRadio, InputCheckbox, FieldSet
    }
}
</script>

<style scoped>
@layer components {
    .inputs > *:nth-child(odd) {
        @apply lg:mr-4;
    }

    .inputs > *:nth-child(even) {
        @apply lg:ml-4;
    }
}
</style>