<template>
  <div class="dashboard-container" @click="closeContextMenu">
    
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
          <div class="vinyl-container"
            @contextmenu.prevent="openContextMenu"
            @click="handleContainerClick">
            
            <!-- 1. The Album Sleeve (On Top) -->
            <div class="album-sleeve">
              <img v-if="currentTrack.cover" :src="currentTrack.cover" class="sleeve-art" />
              <div v-else class="sleeve-placeholder">🎵</div>
            </div>

            <!-- 2. The Vinyl Record (Tucked Underneath, Peeking Right) -->
            <div class="vinyl-record" :class="[{ spinning: isPlaying || isDetecting }, activeVinylStyle]">
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
        <div v-for="style in vinylOptions" :key="style.class" class="menu-item" @click="activeVinylStyle = style.class">
          {{ style.name }}
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useThemeStore } from '../stores/theme';
import { useDashboard } from '../composables/useDashboard';
import '../styles/dashboard.css';

const themeStore = useThemeStore();

const { 
  authStore, showUserMenu, activeTab, isPlaying, isDetecting, 
  hoursPlayed, totalClicks, currentClicks, currentRMS, currentTrack,
  trackTime, clickHistory, trackDuration, formatTime,
  toggleUserMenu, handleLogout, triggerManualDetect 
} = useDashboard();

const showMenu = ref(false);
const menuX = ref(0);
const menuY = ref(0);
const activeVinylStyle = ref('v-classic'); // Default

const vinylOptions =[
  { name: 'Classic Black', class: 'v-classic' },
  { name: 'Bone (Ivory)', class: 'v-bone' },
  { name: 'Ruby Red', class: 'v-ruby' },
  { name: 'Opaque Canary Yellow', class: 'v-canary' },
  { name: 'Orange Crush', class: 'v-orange' },
  { name: 'Electric Blue', class: 'v-electric-blue' },
  { name: 'Royal Blue', class: 'v-royal-blue' },
  { name: 'Kelly Green', class: 'v-kelly-green' },
  { name: 'Rasta Split', class: 'v-rasta-split' },

  { name: 'Galaxy Splash', class: 'v-galaxy-splash' },
  { name: 'Blue w/ Eggyoke', class: 'v-blue-eggyoke' },
  { name: 'Gold Nugget', class: 'v-gold-nugget' },
  { name: 'Blood Fire', class: 'v-blood-fire' },
];

const openContextMenu = (e) => {
  const safeX = Math.min(e.clientX, window.innerWidth - 220); 
  menuX.value = safeX;
  menuY.value = e.clientY;
  showMenu.value = true;
};

const closeContextMenu = () => {
  showMenu.value = false;
};

// --- (POPCORN FIRE) ---
const clickCount = ref(0);
let clickTimeout = null;
const fireEmojis = ref([]);
let fireId = 0;

const handleContainerClick = (e) => {
  if (themeStore.styleMode !== 'modern') return;

  clickCount.value++;
  if (clickTimeout) clearTimeout(clickTimeout);
  clickTimeout = setTimeout(() => { clickCount.value = 0; }, 400);

  if (clickCount.value >= 5) {
    triggerPopcorn(e);
    clickCount.value = 0;
  }
};

const triggerPopcorn = (e) => {
  const container = e.currentTarget.getBoundingClientRect();
  
  for (let i = 0; i < 30; i++) {
    const id = fireId++;
    fireEmojis.value.push({
      id: id,
      x: (Math.random() * container.width),
      y: (Math.random() * container.height) + 20,
      scale: 0.8 + (Math.random() * 0.8),
      duration: 0.6 + (Math.random() * 0.8)
    });

    setTimeout(() => {
      fireEmojis.value = fireEmojis.value.filter(f => f.id !== id);
    }, 1500);
  }
};
</script>