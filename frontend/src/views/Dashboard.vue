<template>
  <div class="dashboard-container" @click="closeContextMenu">
    
    <!-- HEADER -->
    <header class="top-nav">
      <div class="logo">
        <span style="font-size: 1.5rem;">🎵</span> 
        <span style="font-weight: bold; margin-left: 10px;">Smart Turntable</span>
      </div>
      
      <div class="user-menu" @click="router.push('/profile')" style="cursor: pointer;" title="Go to Profile">
        <div class="avatar-circle">
          {{ authStore.user ? 'U' : '?' }}
        </div>
      </div>
    </header>

    <!-- MAIN GRID -->
    <main class="main-grid">
      
      <!-- LEFT: PLAYER -->
      <section class="panel left-panel">
        <div class="visualizer-wrapper">
          <div class="vinyl-container no-select"
            :class="{ 'paused-pulse': isPaused }" 
            @contextmenu.prevent="openContextMenu"
            @click="handleContainerClick">
            
            <!-- 1. The Album Sleeve (On Top) -->
            <div class="album-sleeve">
              <img v-if="currentTrack.cover" :src="currentTrack.cover" class="sleeve-art" />
              <div v-else class="sleeve-placeholder">🎵</div>
            </div>

            <!-- 2. The Vinyl Record (Tucked Underneath, Peeking Right) -->
            <div class="vinyl-record" :class="[{ spinning: isPlaying || isDetecting }, currentTrack.color || 'v-classic']">
              <div class="record-label">
                 <!-- Put a tiny version of the cover on the record label too! -->
                 <img v-if="currentTrack.cover" :src="currentTrack.cover" />
              </div>
            </div>

            <div v-for="fire in fireEmojis" :key="fire.id" class="fire-emoji"
                 :style="{ left: fire.x + 'px', top: fire.y + 'px', transform: `scale(${fire.scale})`, animationDuration: `${fire.duration}s` }">
              🔥
            </div>

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
          <p v-if="!currentTrack.title" class="placeholder-text">
            Waiting for song identification...
          </p>
          <p v-else-if="parsedLyrics.length === 0" class="placeholder-text">
            No lyrics found for {{ currentTrack.title }}.
          </p>
          
          <div v-else class="lyrics-scroll" ref="lyricsContainerRef">
             <p 
                v-for="(line, index) in parsedLyrics" 
                :key="index"
                class="lyric-line"
                :class="{ 'active-lyric': index === activeLyricIndex }"
             >
                {{ line.text || '-' }}
             </p>
          </div>
        </div>

        <!-- DIAGNOSTICS TAB -->
        <div v-if="activeTab === 'diagnostics'" class="tab-content">
          
          <div class="stat-item">
            <span class="stat-label">System Status</span>
            <div class="stat-value" :style="{ color: isPlaying ? 'var(--success)' : 'var(--text-muted)' }">
              {{ isPlaying ? (isPaused ? 'MUSIC IS PAUSED' : "ACTIVE STREAM") : 'IDLE' }}
            </div>
          </div>

          <div class="stat-item">
             <span class="stat-label">Remaining cartridge Hours</span>
             
            <div class="stat-value">
              {{ Math.max(0, 1000 - hoursPlayed).toFixed(1) }} h
            </div>

            <div class="bar-container rtl">

              <div
                class="bar-fill"
                :class="{ low: isLowRemaining }"
                :style="{ width: remainingPercent + '%' }"
                title="Remaining"
              ></div>


            </div>
          </div>

          <div class="stat-item">
             <div style="display:flex; justify-content:space-between; align-items:center;">
                <span class="stat-label">Detected Clicks (Session)</span>
                <!-- Flash Red if current click > 0 -->
                <span class="stat-label" :style="{ color: currentClicks > 0 ? 'red' : 'inherit', fontWeight: 'bold' }">
                   {{ totalClicks }}
                </span>
             </div>
             <div class="timeline-container">
                <div 
                    class="timeline-playhead" 
                    :style="{ left: (trackTime / trackDuration) * 100 + '%' }"
                ></div>
                <div 
                    v-for="(click, index) in clickHistory" 
                    :key="index"
                    class="click-dot"
                    :style="{ left: (click.time / trackDuration) * 100 + '%' }"
                    :title="`Click at ${formatTime(click.time)}`"
                ></div>
             </div>
             <p style="font-size: 0.8rem; color: var(--text-muted); text-align: right; margin-top: 5px;">
                Visualizing clicks over time
             </p>
          </div>

          <div class="stat-item">
             <span class="stat-label">Audio Signal (RMS)</span>
             <div class="bar-container" style="height: 20px;">
                <div class="bar-fill" :style="{ width: (currentRMS * 500) + '%' }"></div>
             </div>
          </div>

        </div>

      </section>
    </main>

    <div v-if="showMenu" class="custom-context-menu" :style="{ left: menuX + 'px', top: menuY + 'px' }">
      <div class="menu-header">Select Vinyl Style</div>
      <div class="menu-scroll">
        <div v-for="style in vinylOptions" :key="style.class" class="menu-item" 
             @click="setVinylColor(style.class); closeContextMenu()">
          {{ style.name }}
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { useThemeStore } from '../stores/theme';
import { useDashboard } from '../composables/useDashboard';
import { useVinylInteractions } from '../composables/useDashboard';
import '../styles/dashboard.css';

const themeStore = useThemeStore()

const { 
  authStore, showUserMenu, router, activeTab, isPlaying, isPaused,
  isDetecting, hoursPlayed, totalClicks, currentClicks, currentRMS, currentTrack,
  trackTime, clickHistory, trackDuration, formatTime,
  toggleUserMenu, handleLogout, triggerManualDetect, setVinylColor,
  parsedLyrics, activeLyricIndex, lyricsContainerRef, maxHours,
  lowThreshold, remainingHours, remainingPercent, isLowRemaining,
} = useDashboard();

const {
  showMenu, menuX, menuY, activeVinylStyle, vinylOptions,
  openContextMenu, closeContextMenu,
  clickCount, fireEmojis, handleContainerClick, triggerPopcorn
} = useVinylInteractions(themeStore);
</script>
