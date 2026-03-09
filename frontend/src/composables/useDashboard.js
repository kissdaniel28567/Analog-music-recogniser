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

    onMounted(() => {
        socket = io('http://localhost:5000');

        // 1. LIVE STATS
        socket.on('stats_update', (data) => {
            // Basic stats
            isPlaying.value = !!data.is_playing;
            currentRMS.value = data.rms || 0;
            hoursPlayed.value = data.total_hours || 0;

            // Track info
            trackTime.value = data.track_time || 0;
            // TODO: This may not work when backend sends proper track length
            if (data.track_duration) trackDuration.value = data.track_duration;

            // Clicks
            currentClicks.value = data.click_count_now || 0;
            clickHistory.value = data.click_history || [];
            totalClicks.value = clickHistory.value.reduce((sum, item) => sum + item.count, 0);
            
            // TODO: might not need this in the future
            trackTime.value = data.track_time || 0;
            
            if (data.current_track && data.current_track.title) {
                currentTrack.value = data.current_track;
            } else if (!isDetecting.value) {
                // TODO: Clear data if we are not busy looking for it
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