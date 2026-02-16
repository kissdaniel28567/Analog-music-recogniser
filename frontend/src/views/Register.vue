<template>
  <div class="auth-container">
    <div class="card auth-card">
      <h2>📝 Register</h2>
      <form @submit.prevent="handleRegister">
        <input v-model="username" placeholder="Choose Username" required />
        <input v-model="password" type="password" placeholder="Choose Password" required />
        <button type="submit">Create Account</button>
      </form>
      <p v-if="error" class="error">{{ error }}</p>
      
      <p class="switch-link">
        Already have an account? 
        <router-link to="/login">Login here</router-link>
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

const handleRegister = async () => {
    const success = await authStore.register(username.value, password.value);
    if (success) {
        router.push('/dashboard');
    } else {
        error.value = "Registration failed (Username might be taken)";
    }
};
</script>

<style scoped>
.auth-container { display: flex; justify-content: center; align-items: center; min-height: 80vh; }
.auth-card { width: 100%; max-width: 400px; }
.switch-link { margin-top: 15px; text-align: center; font-size: 0.9rem; }
.error { color: red; text-align: center; margin-top: 10px; }
</style>