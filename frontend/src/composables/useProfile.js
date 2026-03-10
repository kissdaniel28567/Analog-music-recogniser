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

    return {
        router,
        profileData,
        settings,
        devices,
        isSaving,
        saveSettings,
        handleLogout
    }
}
