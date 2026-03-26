import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '../stores/auth';
import api from '../services/api';

export function useProfile() {
    const router = useRouter();
    const authStore = useAuthStore();
    
    const profileData = ref({ username: '', history: [], cartridges:[] });
    const settings = ref({ rms_threshold: 0.01, click_sensitivity: 15, audio_device_id: null });
    const devices = ref([]);
    const isSaving = ref(false);
    const expandedCartId = ref(null);
    
    const loadData = async () => {
        try {
            const [profileRes, deviceRes] = await Promise.all([
                api.getProfile(),
                api.getAudioDevices()
            ]);
            profileData.value = profileRes.data;
            settings.value = profileRes.data.settings;
            devices.value = deviceRes.data;
        } catch (e) {
            console.error("Failed to load profile data", e);
        }
    };
    
    const saveSettings = async () => {
        isSaving.value = true;
        try {
            await api.updateSettings(settings.value);
            alert("Settings saved successfully!");
        } catch (e) {
            alert("Error saving settings.");
        }
        isSaving.value = false;
    };
    
    const handleLogout = async () => {
        await authStore.logout();
        router.push('/login');
    };
    
    onMounted(() => {
        loadData();
    });

    const resetCartridge = async (id) => {
        if (confirm("Are you sure you want to reset this cartridge's hours to 0?")) {
            try {
                await api.resetCartridge(id);
                loadData(); 
            } catch (e) {
                alert("Failed to reset hours.");
            }
        }
    };

    const updateCartridgeLimit = async (id, recommended_hours) => {
        try {
            await api.updateCartridgeLimit(id, recommended_hours);
            alert("Cartridge settings saved!");
            expandedCartId.value = null;
        } catch (e) {
            alert("Failed to update limit.");
    }
    };

    const toggleCartridge = (id) => {
        if (expandedCartId.value === id) {
            expandedCartId.value = null;
        } else {
            expandedCartId.value = id;
        }
    };

    return {
        router,
        profileData,
        settings,
        devices,
        isSaving,
        expandedCartId,
        saveSettings,
        handleLogout,
        resetCartridge,
        updateCartridgeLimit,
        toggleCartridge
    }
}
