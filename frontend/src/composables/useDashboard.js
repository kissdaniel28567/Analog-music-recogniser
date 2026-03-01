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
    const currentRMS = ref(0);
    const currentTrack = ref({ title: '', artist: '', cover: null });

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

    // --- LIFECYCLE (Will remove after debugging) ---
    onMounted(() => {
        socket = io('http://localhost:5000');
        //console.log("DEBUG: Refresh happened");
        // 1. LIVE STATS
        socket.on('stats_update', (data) => {
            isPlaying.value = !!data.is_playing;
            totalClicks.value = data.clicks || 0;
            currentRMS.value = data.rms || 0;
            hoursPlayed.value = data.total_hours || 0;
            //console.log("DEBUG: Refresh stats update happened");
            
            // TODO: POLISH THIS Auto-detect Logic
            if (data.is_playing) {
                //console.log("DEBUG: Refresh in isplaying update happened");
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
            // DEBUG LOG: Remove this later
            //console.log("DEBIG: Stats received:", data.is_playing, data.rms);
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
        currentRMS,
        currentTrack,
        toggleUserMenu,
        handleLogout,
        triggerManualDetect
    };
}