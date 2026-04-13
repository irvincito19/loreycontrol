const API_URL = '/api';

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
        throw new Error(error.detail || 'Error en la petición');
    }

    if (response.status === 204) return null;
    return response.json();
}

export const api = {
    auth: {
        login: async (formData: FormData) => {
            const response = await fetch(`${API_URL}/auth/login`, {
                method: 'POST',
                body: formData,
            });
            if (!response.ok) throw new Error('Credenciales inválidas');
            return response.json();
        },
        me: () => request('/auth/me'),
    },
    patients: {
        list: () => request('/patients/'),
        get: (id: number) => request(`/patients/${id}`),
        create: (data: any) => request('/patients/', { method: 'POST', body: JSON.stringify(data) }),
        update: (id: number, data: any) => request(`/patients/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
        delete: (id: number) => request(`/patients/${id}`, { method: 'DELETE' }),
    },
    appointments: {
        list: (start?: string, end?: string) => {
            let url = '/appointments/';
            const params = new URLSearchParams();
            if (start) params.append('start_date', start);
            if (end) params.append('end_date', end);
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
        getConfig: () => request('/availability/config'),
        updateConfig: (data: any) => request('/availability/config', { method: 'POST', body: JSON.stringify(data) }),
        getSlots: (date: string) => request(`/availability/slots?date=${date}`),
        updateOverride: (data: any) => request('/availability/overrides', { method: 'POST', body: JSON.stringify(data) }),
    }
};
