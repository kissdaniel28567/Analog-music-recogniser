<template>
  <div class="dashboard">
    <h1>🎧 Dashboard</h1>
    
    <div class="stats-grid">
      <div class="card">
        <h3>Current Status</h3>
        <p class="status" :class="{ playing: isPlaying }">
          {{ isPlaying ? '🎵 Playing' : '🛑 Idle' }}
        </p>
      </div>

      <div class="card">
        <h3>Cartridge Wear</h3>
        <p>{{ hoursPlayed.toFixed(2) }} Hours</p>
      </div>

      <div class="card">
        <h3>Total Clicks (Pops)</h3>
        <p>{{ totalClicks }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import { io } from "socket.io-client";

// State variables
const isPlaying = ref(False);
const hoursPlayed = ref(0);
const totalClicks = ref(0);
let socket = null;

onMounted(() => {
    socket = io('http://localhost:5000');

    socket.on('connect', () => {
        console.log("✅ Connected to WebSocket!");
    });

    socket.on('stats_update', (data) => {
        isPlaying.value = data.is_playing;
        hoursPlayed.value = data.hours;
        totalClicks.value = data.clicks;
    });
});

onUnmounted(() => {
    if (socket) socket.disconnect();
});
</script>

<style scoped>
.stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; }
.card { background: #f4f4f4; padding: 20px; border-radius: 8px; text-align: center; }
.status.playing { color: green; font-weight: bold; }
</style>