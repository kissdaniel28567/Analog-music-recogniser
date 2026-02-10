<template>
  <div class="login-container">
    <h2>Login to Smart Turntable</h2>
    <form @submit.prevent="handleLogin">
      <input v-model="username" placeholder="Username" required />
      <input v-model="password" type="password" placeholder="Password" required />
      <button type="submit">Login</button>
    </form>
    <p v-if="error" class="error">{{ error }}</p>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useAuthStore } from '../stores/auth';
import { useRouter } from 'vue-router';

const username = ref('');
const password = ref('');
const error = ref('');
const authStore = useAuthStore();
const router = useRouter();

const handleLogin = async () => {
    const success = await authStore.login(username.value, password.value);
    if (success) {
        router.push('/dashboard');
    } else {
        error.value = "Invalid credentials";
    }
};
</script>

<style scoped>
.login-container { max-width: 300px; margin: 50px auto; display: flex; flex-direction: column; gap: 10px; }
</style>