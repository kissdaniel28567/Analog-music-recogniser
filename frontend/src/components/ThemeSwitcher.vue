<template>
  <div class="theme-switcher">
    <button @click="themeStore.toggleStyleMode" class="switch-btn">
      {{ themeStore.styleMode === 'modern' ? '💾 Go Retro' : '🚀 Go Modern' }}
    </button>
    <button @click="themeStore.toggleDarkMode" class="switch-btn">
      {{ themeStore.isDark ? '☀️ Light' : '🌙 Dark' }}
    </button>
  </div>
</template>

<script setup>
import { useThemeStore } from '../stores/theme';
const themeStore = useThemeStore();
</script>

<style scoped>
.theme-switcher {
  position: fixed;
  bottom: 20px;
  right: 20px;
  display: flex;
  gap: 10px;
  z-index: 1000;
}
.switch-btn {
  width: auto;
  padding: 8px 16px;
  font-size: 0.8rem;
  opacity: 0.9;
}
</style>