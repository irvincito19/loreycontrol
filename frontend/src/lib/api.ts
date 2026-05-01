const API_URL = import.meta.env.VITE_API_URL || '/api';

export async function request(path: string, options: RequestInit = {}) {
    const token = localStorage.getItem('token');
    const headers = {
        'Content-Type': 'application/json',
        ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
        ...options.headers,
    };

    const response = await fetch(`${API_URL}${path}`, {
        ...options,
        headers,
    });

    if (response.status === 401) {
        localStorage.removeItem('token');
        window.location.hash = '#/login';
    }

    if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: 'Error desconocido' }));
        let message = 'Error en la petición';
        
        if (typeof error.detail === 'string') {
            message = error.detail;
        } else if (Array.isArray(error.detail)) {
            message = error.detail.map((d: any) => `${d.loc.join('.')}: ${d.msg}`).join('\n');
        } else if (error.message) {
            message = error.message;
        }
        
        throw new Error(message);
    }

    if (response.status === 204) return null;
    return response.json();
}

export const api = {
    auth: {
        login: async (formData: FormData) => {
            const params = new URLSearchParams();
            formData.forEach((value, key) => {
                params.append(key, value.toString());
            });

            const response = await fetch(`${API_URL}/auth/login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: params,
            });
            if (!response.ok) throw new Error('Credenciales inválidas');
            return response.json();
        },
        me: () => request('/auth/me'),
        listUsers: () => request('/auth/users'),
        updateUser: (id: number, data: any) => request(`/auth/users/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
    },
    patients: {
        list: () => request('/patients/'),
        get: (id: number) => request(`/patients/${id}`),
        create: (data: any) => request('/patients/', { method: 'POST', body: JSON.stringify(data) }),
        update: (id: number, data: any) => request(`/patients/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
        delete: (id: number) => request(`/patients/${id}`, { method: 'DELETE' }),
    },
    appointments: {
        list: (start?: string, end?: string, location?: string) => {
            let url = '/appointments/';
            const params = new URLSearchParams();
            if (start) params.append('start_date', start);
            if (end) params.append('end_date', end);
            if (location) params.append('location', location);
            if (params.toString()) url += `?${params.toString()}`;
            return request(url);
        },
        create: (data: any) => request('/appointments/', { method: 'POST', body: JSON.stringify(data) }),
        update: (id: number, data: any) => request(`/appointments/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
        delete: (id: number) => request(`/appointments/${id}`, { method: 'DELETE' }),
    },
    payments: {
        list: () => request('/payments/'),
        listByPatient: (id: number) => request(`/payments/patient/${id}`),
        create: (data: any) => request('/payments/', { method: 'POST', body: JSON.stringify(data) }),
    },
    availability: {
        getConfig: (location?: string) => request(`/availability/config${location ? `?location=${location}` : ''}`),
        updateConfig: (data: any) => request('/availability/config', { method: 'POST', body: JSON.stringify(data) }),
        getSlots: (date: string, location: string) => request(`/availability/slots?date=${date}&location=${location}`),
        getOverrides: (date: string, location: string) => request(`/availability/overrides/${date}?location=${location}`),
        updateDayAvailability: (data: any, location: string) => request(`/availability/overrides/bulk?location=${location}`, { method: 'POST', body: JSON.stringify(data) }),
    },
    reminders: {
        getConfig: () => request('/reminders/config'),
        updateConfig: (data: any) => request('/reminders/config', { method: 'POST', body: JSON.stringify(data) }),
    }
};
