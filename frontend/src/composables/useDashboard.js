import { ref, computed, watch, onMounted, onUnmounted, onBeforeUnmount } from 'vue';
import { useAuthStore } from '../stores/auth';
import { useRouter } from 'vue-router';
import { io } from "socket.io-client";

export function useDashboard() {
    const authStore = useAuthStore();
    const router = useRouter();
    const showUserMenu = ref(false);
    const activeTab = ref('diagnostics');

    const isPlaying = ref(false);
    const isDetecting = ref(false);
    const isPaused = ref(false);
    const hoursPlayed = ref(0);
    const totalClicks = ref(0);
    const currentClicks = ref(0);
    const currentRMS = ref(0);
    const currentTrack = ref({ title: '', artist: '', cover: null, color: 'v-classic' });
    const trackTime = ref(0);
    const trackDuration = ref(180);
    const clickHistory = ref([]);
    const parsedLyrics = ref([]);
    const lyricsContainerRef = ref(null);

    let socket = null;

    const toggleUserMenu = () => {
        showUserMenu.value = !showUserMenu.value;
    };

    const handleLogout = async () => {
        await authStore.logout();
        router.push('/login');
    };

    const triggerManualDetect = () => {
        if (isDetecting.value) return;
        console.log("🚀 Manual detection requested...");
        if (socket) socket.emit('manual_detect');
        // server should change this in next iter. Might need to delete this
        isDetecting.value = true;
    };

    const formatTime = (seconds) => {
        if (!seconds) return "00:00";
        const mins = Math.floor(seconds / 60);
        const secs = Math.floor(seconds % 60);
        return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    };

    // ============ DISPLAY FOR LYRICS ============
    const parseLRC = (lrcString) => {
        if (!lrcString) return[];
        const lines = lrcString.split('\n');
        const parsed = [];
        const regex = /\[(\d{2}):(\d{2}(?:\.\d+)?)\](.*)/;

        lines.forEach(line => {
            const match = regex.exec(line);
            if (match) {
                const minutes = parseInt(match[1], 10);
                const seconds = parseFloat(match[2]);
                const text = match[3].trim();
                parsed.push({ time: (minutes * 60) + seconds, text: text });
            } else if (line.trim() !== '') {
                // === CONFIG FOR UNSYNCED LYRICS ===
                parsed.push({ time: -1, text: line.trim() });
            }
        });
        return parsed;
    };

    const activeLyricIndex = computed(() => {
        if (!parsedLyrics.value.length || parsedLyrics.value[0].time === -1) return -1;
        
        for (let i = parsedLyrics.value.length - 1; i >= 0; i--) {
            if (trackTime.value >= parsedLyrics.value[i].time) {
                return i;
            }
        }
        return 0;
    });

    watch(activeLyricIndex, (newIndex) => {
        if (newIndex >= 0 && lyricsContainerRef.value) {
            const activeEl = lyricsContainerRef.value.querySelector('.active-lyric');
            if (activeEl) {
                activeEl.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }
        }
    });

    onMounted(() => {
        socket = io('http://localhost:5000');

        // ============ LIVE STATS ============
        socket.on('stats_update', (data) => {
            // Basic stats
            isPlaying.value = !!data.is_playing;
            isPaused.value = !!data.is_paused;
            currentRMS.value = data.rms || 0;
            hoursPlayed.value = data.total_hours || 0;

            // Track info
            trackTime.value = data.track_time || 0;
            if (data.track_duration) trackDuration.value = data.track_duration;

            // Clicks
            currentClicks.value = data.click_count_now || 0;
            clickHistory.value = data.click_history || [];
            totalClicks.value = clickHistory.value.reduce((sum, item) => sum + item.count, 0);
            trackTime.value = data.track_time || 0;
            
            if (data.current_track && data.current_track.title) {
                currentTrack.value = data.current_track;
                parsedLyrics.value = parseLRC(data.current_track.lyrics);
            } else if (!isDetecting.value) {
                // TODO: Clear data if we are not busy looking for it
            }
        });

        // ============ STATUS CHANGE ============ 
        socket.on('status_change', (data) => {
            if (data.status === 'identifying') {
                isDetecting.value = true;
            } else {
                isDetecting.value = false;
            }
        });

        // ============ TRACK RESULT ============ 
        socket.on('track_identified', (match) => {
            if (match) {
                currentTrack.value = match;
            }
            isDetecting.value = false;
        });
    });

    onUnmounted(() => {
        if (socket) socket.disconnect();
    });

    // ============ VINYL COLOR CHANGE ============ 
    const setVinylColor = (colorClass) => {
        if (!currentTrack.value.title) return;
        
        currentTrack.value.color = colorClass; 
        
        if (socket) {
            socket.emit('set_vinyl_color', { color: colorClass });
        }
    };



    return {
        authStore,
        showUserMenu,
        router,
        activeTab,
        isPlaying,
        isPaused,
        isDetecting,
        hoursPlayed,
        totalClicks,
        currentClicks,
        currentRMS,
        currentTrack,
        trackTime,
        trackDuration,
        clickHistory,
        parsedLyrics,
        activeLyricIndex,
        lyricsContainerRef,
        formatTime,
        toggleUserMenu,
        handleLogout,
        triggerManualDetect,
        setVinylColor
    };
}


export function useVinylInteractions(themeStore, { contextMenuWidth = 220 } = {}) {
  // --- Context menu state ---
  const showMenu = ref(false);
  const menuX = ref(0);
  const menuY = ref(0);
  const activeVinylStyle = ref('v-classic'); // Default

  const vinylOptions = [
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
    const w = typeof window !== 'undefined' ? window.innerWidth : 0;
    const safeX = Math.min(e.clientX, Math.max(0, w - contextMenuWidth));
    menuX.value = safeX;
    menuY.value = e.clientY;
    showMenu.value = true;
  };

  const closeContextMenu = () => {
    showMenu.value = false;
  };

  const clickCount = ref(0);
  let clickTimeout = null;
  const fireEmojis = ref([]);
  let fireId = 0;

  const handleContainerClick = (e) => {
    if (themeStore?.styleMode !== 'modern') return;

    clickCount.value++;
    if (clickTimeout) clearTimeout(clickTimeout);
    clickTimeout = setTimeout(() => {
      clickCount.value = 0;
      clickTimeout = null;
    }, 400);

    if (clickCount.value >= 5) {
      triggerPopcorn(e);
      clickCount.value = 0;
    }
  };

  const activeTimeouts = new Set();

  const triggerPopcorn = (e) => {
    const rect = e.currentTarget?.getBoundingClientRect?.();
    if (!rect) return;

    for (let i = 0; i < 30; i++) {
      const id = fireId++;
      fireEmojis.value.push({
        id,
        x: Math.random() * rect.width,
        y: Math.random() * rect.height + 20,
        scale: 0.8 + Math.random() * 0.8,
        duration: 0.6 + Math.random() * 0.8,
      });

      const t = setTimeout(() => {
        fireEmojis.value = fireEmojis.value.filter((f) => f.id !== id);
        activeTimeouts.delete(t);
      }, 1500);

      activeTimeouts.add(t);
    }
  };

  onBeforeUnmount(() => {
    if (clickTimeout) clearTimeout(clickTimeout);
    activeTimeouts.forEach(clearTimeout);
    activeTimeouts.clear();
  });

  return {
    showMenu,
    menuX,
    menuY,
    activeVinylStyle,
    vinylOptions,
    openContextMenu,
    closeContextMenu,
    clickCount,
    fireEmojis,
    handleContainerClick,
    triggerPopcorn,
  };
}
