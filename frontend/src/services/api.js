import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true,
})

// Add token to requests
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Handle token expiration
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Avoid redirect loop for login endpoint: let login component handle errors
      const reqUrl = error.config?.url || ''
      const reqMethod = (error.config?.method || '').toLowerCase()
      if (!(reqMethod === 'post' && reqUrl.includes('/users/login'))) {
        localStorage.removeItem('token')
        localStorage.removeItem('user')
        window.location.href = '/login'
      }
    }
    return Promise.reject(error)
  }
)

export const authAPI = {
  login: (credentials) => api.post('/users/login', credentials),
  register: (userData) => api.post('/users/register', userData),
  verifyEmail: (verificationData) => api.post('/users/verify-email', verificationData),
  getProfile: () => api.get('/users/me'),
}

export const eventsAPI = {
  getEvents: () => api.get('/events'),
  getEventsByUser: (userId) => api.get(`/events/user/${userId}`),
  getEvent: (id) => api.get(`/events/${id}`),
  createEvent: (eventData) => api.post('/events', eventData),
  updateEvent: (id, eventData) => api.put(`/events/${id}`, eventData),
  deleteEvent: (id) => api.delete(`/events/${id}`),
}

export const nlpAPI = {
  parseText: (text) => api.post('/nlp/parse', { text }),
}

export default api