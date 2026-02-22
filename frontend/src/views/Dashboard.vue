<template>
  <div class="dashboard-container">

    <header class="top-nav">
      <div class="logo">🎵 Smart Turntable</div>

      <div class="user-menu" @click="toggleUserMenu">
        <div class="avatar-circle">
          {{ authStore.user ? 'U' : '?' }}
        </div>

        <div v-if="showUserMenu" class="dropdown-menu">
          <div class="dropdown-item">Settings</div>
          <div class="dropdown-item danger" @click="handleLogout">Logout</div>
        </div>
      </div>
    </header>

    <!-- 2. MAIN SPLIT LAYOUT -->
    <main class="main-grid">

      <!-- LEFT COLUMN: Player & Detection -->
      <section class="panel left-panel">
        <div class="visualizer-box">
          <!-- TODO: Animation -->
          <div class="vinyl-record" :class="{ spinning: isPlaying }">
            <div class="label"></div>
          </div>
        </div>

        <div class="track-info">
          <h2>{{ currentTrack.title || "No Music Detected" }}</h2>
          <h3>{{ currentTrack.artist || "Waiting for needle drop..." }}</h3>
        </div>

        <div class="controls">
          <button class="detect-btn" @click="triggerManualDetect" :disabled="isDetecting">
            {{ isDetecting ? 'Listening...' : '🔍 Detect Now' }}
          </button>
        </div>
      </section>

      <!-- RIGHT COLUMN: Tabs & Info -->
      <section class="panel right-panel">

        <!-- Tab Headers -->
        <div class="tabs-header">
          <button :class="{ active: activeTab === 'lyrics' }" @click="activeTab = 'lyrics'">
            🎤 Lyrics
          </button>
          <button :class="{ active: activeTab === 'maintenance' }" @click="activeTab = 'maintenance'">
            🛠️ Diagnostics
          </button>
        </div>

        <!-- Tab Content: LYRICS -->
        <div v-if="activeTab === 'lyrics'" class="tab-content lyrics-area">
          <p v-if="!currentTrack.title" class="placeholder-text">
            Play a record to see lyrics here...
          </p>
          <div v-else class="lyrics-scroll">
            <!-- TODO: Lyrics -->
            <p>This is where the synced lyrics will appear.</p>
            <p>Line 2 of the song...</p>
            <p class="highlight">Line 3 (Currently singing)</p>
            <p>Line 4...</p>
          </div>
        </div>

        <!-- Tab Content: MAINTENANCE -->
        <div v-if="activeTab === 'maintenance'" class="tab-content maintenance-area">
          <div class="stat-row">
            <span>Cartridge Health</span>
            <strong>{{ hoursPlayed.toFixed(2) }} Hours</strong>
          </div>
          <div class="progress-bar">
            <div class="fill" :style="{ width: (hoursPlayed / 1000) * 100 + '%' }"></div>
          </div>

          <div class="stat-row">
            <span>Surface Noise (Clicks)</span>
            <strong :class="{ 'text-danger': totalClicks > 50 }">{{ totalClicks }}</strong>
          </div>

          <div class="stat-row">
            <span>Audio Signal (RMS)</span>
            <div class="vu-meter">
              <div class="vu-fill" :style="{ width: (currentRMS * 1000) + '%' }"></div>
            </div>
          </div>
        </div>

      </section>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import { useAuthStore } from '../stores/auth';
import { useRouter } from 'vue-router';
import { io } from "socket.io-client";

// --- STATE ---
const authStore = useAuthStore();
const router = useRouter();
const showUserMenu = ref(false);
const activeTab = ref('lyrics'); // Default tab

// Data from Backend
const isPlaying = ref(false);
const isDetecting = ref(false);
const hoursPlayed = ref(0);
const totalClicks = ref(0);
const currentRMS = ref(0);
const currentTrack = ref({ title: '', artist: '' });

let socket = null;

// --- ACTIONS ---

const toggleUserMenu = () => {
  showUserMenu.value = !showUserMenu.value;
};

const handleLogout = async () => {
  await authStore.logout();
  router.push('/login');
};

const triggerManualDetect = () => {
  isDetecting.value = true;
  // TODO: Call API endpoint here
  console.log("Manual detection requested...");

  // Fake timeout for prototype feel
  setTimeout(() => {
    isDetecting.value = false;
    currentTrack.value = { title: "Bohemian Rhapsody", artist: "Queen" };
    isPlaying.value = true;
  }, 3000);
};

// --- LIFECYCLE (WebSockets) ---

onMounted(() => {
  // Connect to backend
  socket = io('http://localhost:5000');

  socket.on('stats_update', (data) => {
    isPlaying.value = data.is_playing;
    totalClicks.value = data.clicks; // Note: You might want a Cumulative total here later
    currentRMS.value = data.rms;
    hoursPlayed.value = data.total_hours;
  });
});

onUnmounted(() => {
  if (socket) socket.disconnect();
});
</script>

<style scoped>
/* --- LAYOUT --- */
.dashboard-container {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.top-nav {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px;
  height: 60px;
  background-color: var(--bg-card);
  border-bottom: 1px solid var(--border-color);
}

.main-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  /* 50% - 50% split */
  gap: 20px;
  padding: 20px;
  flex-grow: 1;
}

/* On mobile, stack them */
@media (max-width: 768px) {
  .main-grid {
    grid-template-columns: 1fr;
  }
}

.panel {
  background-color: var(--bg-card);
  border-radius: var(--app-radius);
  box-shadow: var(--card-shadow);
  padding: 20px;
  display: flex;
  flex-direction: column;
}

/* --- LEFT PANEL (PLAYER) --- */
.left-panel {
  align-items: center;
  justify-content: center;
  text-align: center;
  gap: 20px;
}

.visualizer-box {
  width: 200px;
  height: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.vinyl-record {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  background: radial-gradient(circle, #111 20%, #333 100%);
  position: relative;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.5);
  border: 4px solid #000;
}

.vinyl-record.spinning {
  animation: spin 4s linear infinite;
}

.label {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 30%;
  height: 30%;
  background-color: var(--primary);
  border-radius: 50%;
}

@keyframes spin {
  100% {
    transform: rotate(360deg);
  }
}

.detect-btn {
  max-width: 200px;
  margin-top: 10px;
}

/* --- RIGHT PANEL (TABS) --- */
.tabs-header {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
  border-bottom: 1px solid var(--border-color);
  padding-bottom: 10px;
}

.tabs-header button {
  background: transparent;
  color: var(--text-muted);
  box-shadow: none;
  width: auto;
  border-radius: var(--modern-btn-radius);
}

.tabs-header button.active {
  background-color: var(--primary);
  color: white;
  box-shadow: var(--btn-shadow);
}

.tab-content {
  flex-grow: 1;
}

/* Lyrics */
.lyrics-area {
  text-align: center;
  overflow-y: auto;
  max-height: 400px;
  font-size: 1.1rem;
  line-height: 1.8;
}

.highlight {
  color: var(--primary);
  font-weight: bold;
  transform: scale(1.05);
  transition: all 0.2s;
}

/* Maintenance */
.stat-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 10px;
  margin-top: 20px;
}

.progress-bar,
.vu-meter {
  height: 10px;
  background-color: var(--bg-input);
  border-radius: 5px;
  overflow: hidden;
}

.fill {
  background-color: var(--primary);
  height: 100%;
  transition: width 0.5s;
}

.vu-fill {
  background-color: var(--success);
  height: 100%;
  transition: width 0.1s;
}

.text-danger {
  color: var(--danger);
}

/* --- USER MENU --- */
.user-menu {
  position: relative;
  cursor: pointer;
}

.avatar-circle {
  width: 40px;
  height: 40px;
  background-color: var(--primary);
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
}

.dropdown-menu {
  position: absolute;
  top: 50px;
  right: 0;
  background-color: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  width: 150px;
  box-shadow: var(--shadow);
  z-index: 100;
}

.dropdown-item {
  padding: 10px;
  border-bottom: 1px solid var(--border-color);
}

.dropdown-item:hover {
  background-color: var(--bg-input);
}

.dropdown-item.danger {
  color: var(--danger);
}
</style>