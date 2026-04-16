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
    const showNewCartModal = ref(false);
    const newCartData = ref({ name: '', recommended_hours: 1000 });

    const LASTFM_API_KEY = "38a0db497a6bcbcc8794b2b12a5dc8fd"; 
    
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
    
    onMounted(async () => {
        const urlParams = new URLSearchParams(window.location.search);
        const token = urlParams.get('token');
        
        if (token) {
            try {
                await api.connectLastFm(token);
                window.history.replaceState({}, document.title, "/profile");
                alert("Last.fm Connected!");
            } catch(e) {
                alert("Failed to connect Last.fm");
            }
        }
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

    const connectLastFm = () => {
        const callbackUrl = window.location.origin + '/profile';
        window.location.href = `http://www.last.fm/api/auth/?api_key=${LASTFM_API_KEY}&cb=${callbackUrl}`;
    };

    const disconnectLastFm = async () => {
        await api.disconnectLastFm();
        loadData(); 
    };

    const addNewCartridge = async () => {
        try {
            await api.addCartridge(newCartData.value);
            showNewCartModal.value = false;
            newCartData.value = { name: '', recommended_hours: 1000 };
            loadData();
        } catch (e) {
            alert("Failed to add cartridge.");
        }
    };
    const activateCartridge = async (id) => {
        try {
            await api.setActiveCartridge(id);
            loadData();
        } catch (e) {
            alert("Failed to activate cartridge.");
        }
    };


    return {
        router,
        profileData,
        settings,
        devices,
        isSaving,
        expandedCartId,
        showNewCartModal,
        newCartData,
        saveSettings,
        handleLogout,
        resetCartridge,
        updateCartridgeLimit,
        toggleCartridge,
        connectLastFm,
        disconnectLastFm,
        addNewCartridge,
        activateCartridge
    }
}
