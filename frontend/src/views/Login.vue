<template>
  <div class="auth-container">
    <div class="card auth-card">
      <!-- Logic is the same as before, just wrapped in new classes -->
      <h2>🔑 Login</h2>
      <form @submit.prevent="handleLogin">
        <input v-model="username" placeholder="Username" required />
        <input v-model="password" type="password" placeholder="Password" required />
        <button type="submit">Enter</button>
      </form>
      <p v-if="error" class="error">{{ error }}</p>

      <p class="switch-link">
        New here? 
        <router-link to="/register">Create an account</router-link>
      </p>
    </div>
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
.auth-container { display: flex; justify-content: center; align-items: center; min-height: 80vh; }
.auth-card { width: 100%; max-width: 400px; }
.switch-link { margin-top: 15px; text-align: center; font-size: 0.9rem; }
.error { color: red; text-align: center; margin-top: 10px; }
</style>