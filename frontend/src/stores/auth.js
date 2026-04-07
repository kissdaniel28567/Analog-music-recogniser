import { defineStore } from 'pinia';
import api from '../services/api';

export const useAuthStore = defineStore('auth', {
    state: () => ({
        user: localStorage.getItem('user_id') || null,
        isAuthenticated: localStorage.getItem('is_auth') === 'true' || false
    }),
    actions: {
        async login(username, password) {
            try {
                const response = await api.login({ username, password });
                this.user = response.data.user_id;
                this.isAuthenticated = true;

                localStorage.setItem('is_auth', 'true');
                localStorage.setItem('user_id', this.user);
                return true;
            } catch (error) {
                console.error("Login failed", error);
                return false;
            }
        },
        async register(username, password) {
            try {
                await api.register({ username, password });
                return await this.login(username, password);
            } catch (error) {
                console.error("Registration failed", error);
                return false;
            }
        },
        async logout() {
            await api.logout();
            this.user = null;
            this.isAuthenticated = false;

            localStorage.removeItem('is_auth');
            localStorage.removeItem('user_id');
        }
    }
});