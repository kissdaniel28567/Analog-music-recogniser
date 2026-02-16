import { defineStore } from 'pinia';

export const useThemeStore = defineStore('theme', {
    state: () => ({
        isDark: localStorage.getItem('theme_dark') === 'true',
        styleMode: localStorage.getItem('theme_style') || 'modern'
    }),
    actions: {
        toggleDarkMode() {
            this.isDark = !this.isDark;
            localStorage.setItem('theme_dark', this.isDark);
        },
        toggleStyleMode() {
            this.styleMode = this.styleMode === 'modern' ? 'retro' : 'modern';
            localStorage.setItem('theme_style', this.styleMode);
        }
    }
});