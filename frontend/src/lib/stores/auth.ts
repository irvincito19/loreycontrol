import { writable } from 'svelte/store';
import { api } from '../api';

function createAuth() {
    const { subscribe, set, update } = writable({
        user: null,
        loading: true,
        authenticated: false
    });

    return {
        subscribe,
        init: async () => {
            const token = localStorage.getItem('token');
            if (!token) {
                set({ user: null, loading: false, authenticated: false });
                return;
            }
            try {
                const user = await api.auth.me();
                set({ user, loading: false, authenticated: true });
            } catch (e) {
                localStorage.removeItem('token');
                set({ user: null, loading: false, authenticated: false });
            }
        },
        login: async (formData: FormData) => {
            const data = await api.auth.login(formData);
            localStorage.setItem('token', data.access_token);
            const user = await api.auth.me();
            set({ user, loading: false, authenticated: true });
            return user;
        },
        logout: () => {
            localStorage.removeItem('token');
            set({ user: null, loading: false, authenticated: false });
            window.location.hash = '#/login';
        }
    };
}

export const auth = createAuth();
