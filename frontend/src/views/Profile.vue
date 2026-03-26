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

        <h2>📀 Cartridge Management</h2>
        <p class="help-text">Manage the lifespan of your needles.</p>

        <div class="cart-list">
          <div v-for="cart in profileData.cartridges" :key="cart.id" class="cart-item" :class="{ active: cart.active }">

            <div class="cart-info">
              <div v-for="cart in profileData.cartridges" :key="cart.id" class="cart-item"
                :class="{ active: cart.active }">

                <div class="cart-header" @click="toggleCartridge(cart.id)">
                  <div class="cart-info">
                    <span class="cart-name">
                      {{ cart.name }}
                      <span v-if="cart.active" class="active-badge">(Active)</span>
                    </span>
                    <span class="cart-usage">{{ cart.hours.toFixed(2) }} / {{ cart.recommended_hours }} Hours
                      Used</span>
                  </div>

                  <div class="expand-icon" :class="{ rotated: expandedCartId === cart.id }">
                    ▼
                  </div>
                </div>

                <div class="cart-settings-panel" v-show="expandedCartId === cart.id">

                  <div class="settings-left">
                    <label>Set Max Lifespan:</label>
                    <div class="input-with-suffix">
                      <input type="number" v-model="cart.recommended_hours" class="limit-input">
                      <span>Hours</span>
                    </div>
                  </div>

                  <div class="settings-right">
                    <button @click="updateCartridgeLimit(cart.id, cart.recommended_hours)" class="btn-save">
                      💾 Save
                    </button>

                    <button @click="resetCartridge(cart.id)" class="btn-warn" title="Reset hours to zero">
                      🔄 Reset Hours
                    </button>
                  </div>

                </div>

              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- RIGHT COLUMN: Settings -->
      <section class="panel">
        <hr class="divider" />
        <h2>🔗 Integrations</h2>
        
        <div class="integration-card">
          <div class="integration-header">
            <div class="integration-logo">
              <!-- Last.fm logó vagy csak stílusos szöveg -->
              <span class="lastfm-icon">last.fm</span>
            </div>
            
            <div v-if="profileData.lastfm?.connected" class="integration-status connected">
              <span class="status-dot"></span> Connected
            </div>
            <div v-else class="integration-status disconnected">
              Not Connected
            </div>
          </div>
          
          <div class="integration-body">
            <div v-if="profileData.lastfm?.connected">
              <p class="integration-text">
                Automatically scrobbling your vinyl records as 
                <strong>{{ profileData.lastfm.username }}</strong>.
              </p>
              <button @click="disconnectLastFm" class="btn-disconnect">Disconnect Account</button>
            </div>
            
            <div v-else>
              <p class="integration-text">
                Connect your Last.fm account to automatically log your physical listening history to your digital profile.
              </p>
              <button @click="connectLastFm" class="btn-lastfm">
                Connect Last.fm
              </button>
            </div>
          </div>
        </div>

        <hr class="divider" />

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
  expandedCartId,
  saveSettings,
  handleLogout,
  updateCartridgeLimit,
  resetCartridge, toggleCartridge,
  connectLastFm, disconnectLastFm,
} = useProfile();
</script>