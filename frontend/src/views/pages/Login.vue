<template>
    <div class="fixed inset-0 md:bg-gray-800 flex items-center justify-center">
        <div class="p-4 md:p-10 bg-white rounded">
            <span class="material-icons text-5xl text-primary flex justify-center mb-4">
                tapas</span>
            <h1 class="mb-6">Sign in to your account</h1>
            <InputText name="Username" type="text" :value="credentials.username" 
                @input="(e)=>credentials.username=e.target.value"/>
            <InputText name="Password" type="password" :value="credentials.password"
                @input="(e)=>credentials.password=e.target.value"/>
            <p class="text-sm text-right">
                Credentials: user / user123</p>
            <Button class="mt-6 w-full" color="primary"
                @click="signIn">
                Sign in
            </Button>
            <div v-if="message.display" class="flex w-full py-4 m-auto">
                <p class="flex-grow text-center text-red-500">
                    {{message.value}}</p>
            </div>
        </div>
    </div>
</template>

<script>
import {reactive} from 'vue'
import {useRouter} from 'vue-router'
import InputText from '@/components/InputText.vue'
import Button from '@/components/Button.vue'

export default {
    components: {
        InputText, Button
    },
    setup() {
        const router = useRouter()
        const credentials = reactive({
            username: '', 
            password: ''
        })
        const message = reactive({
            value: '',
            display: false
        })
        const signIn = ()=> {
            if (credentials.username == 'user' && 
                credentials.password == 'user123')
                router.push({name:'Home'})
            else
                message.value = 'Invalid username and/or password.'
                message.display = true
        }

        return {
            credentials,
            message,
            signIn
        }
    }
}
</script>