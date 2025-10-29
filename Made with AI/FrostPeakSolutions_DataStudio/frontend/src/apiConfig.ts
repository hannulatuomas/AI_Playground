// Centralized API config for frontend
// Always use this for all API endpoints, never hardcode URLs in components!

// Robust environment variable resolution for browser and Node.js
const API_BASE_URL = '/api';

export { API_BASE_URL };


export function getApiUrl(path: string) {
  // Ensures no double slashes
  return `${API_BASE_URL.replace(/\/$/, '')}/${path.replace(/^\//, '')}`;
}
