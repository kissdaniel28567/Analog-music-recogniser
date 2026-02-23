<template>
  <div class="dashboard-container">
    
    <!-- HEADER -->
    <header class="top-nav">
      <div class="logo">
        <span style="font-size: 1.5rem;">🎵</span> 
        <span style="font-weight: bold; margin-left: 10px;">Smart Turntable</span>
      </div>
      
      <div class="user-menu" @click="toggleUserMenu">
        <div class="avatar-circle">
          {{ authStore.user ? 'U' : '?' }}
        </div>
        <div v-if="showUserMenu" class="dropdown-menu">
          <div class="dropdown-item danger" @click="handleLogout">Logout</div>
        </div>
      </div>
    </header>

    <!-- MAIN GRID -->
    <main class="main-grid">
      
      <!-- LEFT: PLAYER -->
      <section class="panel left-panel">
        <div class="visualizer-wrapper">
          <!-- Added Album Art Support -->
          <div class="vinyl-record" :class="{ spinning: isPlaying || isDetecting }">
            <img v-if="currentTrack.cover" :src="currentTrack.cover" class="album-art-overlay" />
            <div class="label"></div>
          </div>
        </div>

        <div class="track-info">
          <!-- Dynamic Text based on State -->
          <h2 v-if="isDetecting">Listening...</h2>
          <h2 v-else>{{ currentTrack.title || "Ready to Play" }}</h2>
          
          <h3 v-if="!isDetecting">{{ currentTrack.artist || "Drop the needle to start" }}</h3>
        </div>

        <div class="controls">
          <button @click="triggerManualDetect" :disabled="isDetecting">
            {{ isDetecting ? 'Identifying...' : '🔍 Detect Now' }}
          </button>
        </div>
      </section>

      <!-- RIGHT: INFO TABS -->
      <section class="panel right-panel">
        
        <div class="tabs-header">
          <button class="tab-btn" :class="{ active: activeTab === 'lyrics' }" @click="activeTab = 'lyrics'">
            LYRICS
          </button>
          <button class="tab-btn" :class="{ active: activeTab === 'diagnostics' }" @click="activeTab = 'diagnostics'">
            DIAGNOSTICS
          </button>
        </div>

        <!-- LYRICS TAB -->
        <div v-if="activeTab === 'lyrics'" class="tab-content lyrics-area">
          <p v-if="!currentTrack.title" style="color: var(--text-muted); margin-top: 50px;">
            Waiting for song identification...
          </p>
          <div v-else>
             <!-- Placeholder for real lyrics later -->
             <p>Lyrics for <strong>{{ currentTrack.title }}</strong> would appear here.</p>
          </div>
        </div>

        <!-- DIAGNOSTICS TAB -->
        <div v-if="activeTab === 'diagnostics'" class="tab-content">
          
          <div class="stat-item">
            <span class="stat-label">System Status</span>
            <div class="stat-value" :style="{ color: isPlaying ? 'var(--success)' : 'var(--text-muted)' }">
              {{ isPlaying ? 'ACTIVE STREAM' : 'IDLE' }}
            </div>
          </div>

          <div class="stat-item">
             <span class="stat-label">Cartridge Hours</span>
             <div class="stat-value">{{ hoursPlayed.toFixed(4) }} h</div>
             <div class="bar-container">
               <!-- Example: 1000 hours max -->
               <div class="bar-fill" :style="{ width: (hoursPlayed / 1000 * 100) + '%' }"></div>
             </div>
          </div>

          <div class="stat-item">
             <span class="stat-label">Detected Clicks/Pops</span>
             <div class="stat-value" :style="{ color: totalClicks > 10 ? 'var(--danger)' : 'inherit'}">
               {{ totalClicks }}
             </div>
          </div>

          <div class="stat-item">
             <span class="stat-label">Audio Signal (RMS)</span>
             <div class="bar-container" style="height: 20px;">
                <div class="bar-fill" :style="{ width: (currentRMS * 500) + '%', backgroundColor: 'var(--success)' }"></div>
             </div>
          </div>

        </div>

      </section>
    </main>
  </div>
</template>

<script setup>
import { useDashboard } from '../composables/useDashboard';
import '../styles/dashboard.css';

const { 
  authStore, 
  showUserMenu, 
  activeTab, 
  isPlaying, 
  isDetecting, 
  hoursPlayed, 
  totalClicks, 
  currentRMS, 
  currentTrack, 
  toggleUserMenu, 
  handleLogout, 
  triggerManualDetect 
} = useDashboard();
</script>