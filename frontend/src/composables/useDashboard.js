import { ref, onMounted, onUnmounted } from 'vue';
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
    const hoursPlayed = ref(0);
    const totalClicks = ref(0);
    const currentClicks = ref(0);
    const currentRMS = ref(0);
    const currentTrack = ref({ title: '', artist: '', cover: null });
    const trackTime = ref(0);
    const trackDuration = ref(180);
    const clickHistory = ref([]);

    const hasAutoDetected = ref(false);
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
        console.log("🚀 Requesting detection...");
        if (socket) socket.emit('manual_detect');
        isDetecting.value = true;
    };

    const formatTime = (seconds) => {
        if (!seconds) return "00:00";
        const mins = Math.floor(seconds / 60);
        const secs = Math.floor(seconds % 60);
        return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    };

    // --- LIFECYCLE (Will remove after debugging) ---
    onMounted(() => {
        socket = io('http://localhost:5000');

        // 1. LIVE STATS
        socket.on('stats_update', (data) => {
            isPlaying.value = !!data.is_playing;
            totalClicks.value = data.clicks || 0;
            currentRMS.value = data.rms || 0;
            hoursPlayed.value = data.total_hours || 0;
            trackTime.value = data.track_time || 0;
            clickHistory.value = data.click_history || [];
            currentClicks.value = data.click_count_now || 0;
            trackTime.value = data.track_time || 0;

            // DEBUG LINE FOR
            console.log("DEBUG: RMS: " + currentRMS.value);
            

            // TODO: This may not work when backend sends proper track length
            if (data.track_duration) {
                trackDuration.value = data.track_duration;
            }

            totalClicks.value = clickHistory.value.reduce((sum, item) => sum + item.count, 0);
            
            // TODO: POLISH THIS Auto-detect Logic
            if (data.is_playing) {
                if (!isDetecting.value && !currentTrack.value.title && !hasAutoDetected.value) {
                    console.log("🎵 Music detected on load/start! Auto-detecting...");
                    triggerManualDetect();
                    hasAutoDetected.value = true;
                }
            } else {
                hasAutoDetected.value = false;
            }
        });

        // 2. STATUS CHANGE
        socket.on('status_change', (data) => {
            if (data.status === 'identifying') {
                isDetecting.value = true;
            } else {
                isDetecting.value = false;
            }
        });

        // 3. TRACK RESULT
        socket.on('track_identified', (match) => {
            if (match) {
                currentTrack.value = match;
                isPlaying.value = true;
            } else {
                console.log("Detection finished, no match found.");
            }
            isDetecting.value = false;
        });
    });

    onUnmounted(() => {
        if (socket) socket.disconnect();
    });

    return {
        authStore,
        showUserMenu,
        activeTab,
        isPlaying,
        isDetecting,
        hoursPlayed,
        totalClicks,
        currentClicks,
        currentRMS,
        currentTrack,
        trackTime,
        trackDuration,
        clickHistory,
        formatTime,
        toggleUserMenu,
        handleLogout,
        triggerManualDetect
    };
}