import { defineStore } from 'pinia';
import api from '../services/api';

export const useAuthStore = defineStore('auth', {
    state: () => ({
        user: null,
        isAuthenticated: false
    }),
    actions: {
        async login(username, password) {
            try {
                const response = await api.login({ username, password });
                this.user = response.data.user_id;
                this.isAuthenticated = true;
                return true;
            } catch (error) {
                console.error("Login failed", error);
                return false;
            }
        },
        async logout() {
            await api.logout();
            this.user = null;
            this.isAuthenticated = false;
        }
    }
});