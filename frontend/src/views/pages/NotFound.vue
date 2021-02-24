<template>
    <div class="fixed inset-0 flex items-center justify-center">
        <div class="p-4 md:p-10">
            <span class="material-icons text-5xl text-primary flex justify-center mb-4">
                mood_bad</span>
            <h1 class="mb-6">Page not found</h1>
            <p>
                <span class="cursor-pointer underline text-primary-dark" 
                    @click="()=>$router.go(-1)">
                    Click here</span>
                to go back.
            </p>
        </div>
    </div>
</template>