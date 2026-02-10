import axios from 'axios';

// Might need to adjust the port depending on the backend.
const apiClient = axios.create({
    baseURL: 'http://localhost:5000',
    withCredentials: true,
    headers: {
        'Content-Type': 'application/json'
    }
});

export default {
    login(credentials) {
        return apiClient.post('/auth/login', credentials);
    },
    register(credentials) {
        return apiClient.post('/auth/register', credentials);
    },
    logout() {
        return apiClient.post('/auth/logout');
    },
    getCartridges() {
        return apiClient.get('/api/cartridges/');
    },
    setActiveCartridge(id) {
        return apiClient.post('/api/cartridges/set_active', { cartridge_id: id });
    }
};