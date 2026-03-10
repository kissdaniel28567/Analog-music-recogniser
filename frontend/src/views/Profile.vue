<template>
  <div class="dashboard-container">
    
    <header class="top-nav">
      <div class="logo">👤 {{ profileData.username }}'s Profile</div>
      <button @click="router.push('/dashboard')" class="btn-secondary">Back to Player</button>
    </header>

    <main class="profile-grid">
      
      <section class="panel">
        <h2>🎵 Listening History</h2>
        <div class="history-list">
          <div v-if="profileData.history.length === 0" class="empty-state">No tracks recorded yet.</div>
          <div v-for="(track, index) in profileData.history" :key="index" class="history-item">
             <div class="track-name">{{ track.title }}</div>
             <div class="track-meta">{{ track.artist }} • {{ track.time }}</div>
          </div>
        </div>

        <h2 style="margin-top: 30px;">📀 Cartridges</h2>
        <div class="cart-list">
          <div v-for="cart in profileData.cartridges" :key="cart.name" class="cart-item" :class="{ active: cart.active }">
             <span>{{ cart.name }}</span>
             <strong>{{ cart.hours.toFixed(2) }} hrs</strong>
          </div>
        </div>
      </section>

      <!-- RIGHT COLUMN: Settings -->
      <section class="panel">
        <h2>⚙️ Hardware Settings</h2>
        
        <form @submit.prevent="saveSettings" class="settings-form">
          
          <div class="form-group">
            <label>Audio Input Device</label>
            <select v-model="settings.audio_device_id">
              <option :value="null">System Default</option>
              <option v-for="dev in devices" :key="dev.id" :value="dev.id">
                [{{ dev.id }}] {{ dev.name }}
              </option>
            </select>
          </div>

          <div class="form-group">
            <label>Music Start Sensitivity (RMS Threshold)</label>
            <span class="help-text">Lower = More sensitive. Current: {{ settings.rms_threshold }}</span>
            <input type="range" v-model="settings.rms_threshold" min="0.001" max="0.1" step="0.001" />
          </div>

          <div class="form-group">
            <label>Click Detection Sensitivity</label>
            <span class="help-text">Lower = Detects more clicks. Current: {{ settings.click_sensitivity }}</span>
            <input type="range" v-model="settings.click_sensitivity" min="5" max="60" step="1" />
          </div>

          <button type="submit" class="btn-primary" :disabled="isSaving">
            {{ isSaving ? 'Saving...' : '💾 Save Settings' }}
          </button>
        </form>

        <div class="logout-section">
          <button @click="handleLogout" class="btn-danger">Logout</button>
        </div>

      </section>

    </main>
  </div>
</template>

<script setup>
import { useProfile } from '../composables/useProfile';
import '../styles/dashboard.css';
import '../styles/profile.css';

const {
    router,
    profileData,
    settings,
    devices,
    isSaving,
    saveSettings,
    handleLogout
} = useProfile();
</script>