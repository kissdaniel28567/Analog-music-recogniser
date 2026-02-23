<template>
  <!-- We apply the data attributes here to control the CSS -->
  <div class="app-root" :data-theme="themeStore.isDark ? 'dark' : 'light'" :data-style="themeStore.styleMode">
    
    <ThemeSwitcher />
    
    <div class="content-wrapper">
      <router-view></router-view>
    </div>

  </div>
</template>

<script setup>
import ThemeSwitcher from './components/ThemeSwitcher.vue';
import { useThemeStore } from './stores/theme';

const themeStore = useThemeStore();
</script>

<style>
.app-root {
  min-height: 100vh;
  width: 100%;
  background-color: var(--bg-body);
  color: var(--text-main);
  transition: background-color 0.3s;
}

.content-wrapper {
  padding: 20px;
}
</style>