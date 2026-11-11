/**
 * Cliente de la API (specs, sección 8). Agrega el token a las llamadas del
 * panel y convierte los errores Problem Details en ApiError.
 */
import { expireSession, getToken } from './auth.js';

const BASE = '/api/v1';

export class ApiError extends Error {
  constructor(status, problem) {
    super(problem?.detail || `Error ${status}`);
    this.status = status;
    this.errors = problem?.errors || {};
  }
}

async function request(path, { method = 'GET', body, json, auth = true, raw = false } = {}) {
  const headers = {};
  const token = getToken();
  if (auth && token) headers.Authorization = `Bearer ${token}`;
  if (json !== undefined) headers['Content-Type'] = 'application/json';

  let response;
  try {
    response = await fetch(BASE + path, {
      method,
      headers,
      body: json !== undefined ? JSON.stringify(json) : body,
    });
  } catch {
    throw new ApiError(0, { detail: 'Sin conexión con el servidor' });
  }

  if (response.status === 401 && auth && token) {
    expireSession();
    throw new ApiError(401, { detail: 'Sesión expirada' });
  }
  if (!response.ok) {
    let problem = null;
    try {
      problem = await response.json();
    } catch {
      // Sin cuerpo JSON: queda el error genérico.
    }
    throw new ApiError(response.status, problem);
  }
  return raw ? response : response.json();
}

export const api = {
  /** RF-09: registro público. */
  register: (formData) => request('/interns', { method: 'POST', body: formData, auth: false }),
  login: (username, password) =>
    request('/auth/login', { method: 'POST', json: { username, password }, auth: false }),
  list: (status) => request(`/interns${status ? `?status=${status}` : ''}`),
  summary: () => request('/interns/summary'),
  get: (id) => request(`/interns/${id}`),
  decide: (id, status, note = '') =>
    request(`/interns/${id}/status`, { method: 'PATCH', json: { status, note } }),

  /** RF-14: se pide con el token y se descarga como archivo. */
  async downloadCv(id) {
    const response = await request(`/interns/${id}/cv`, { raw: true });
    const blob = await response.blob();
    const fileName = fileNameFrom(response.headers.get('Content-Disposition')) || 'hoja-de-vida.pdf';
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = fileName;
    document.body.appendChild(link);
    link.click();
    link.remove();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
  },
};

/** Lee el nombre de Content-Disposition, prefiriendo la versión UTF-8 (filename*). */
export function fileNameFrom(header) {
  if (!header) return null;
  const utf8 = /filename\*=UTF-8''([^;]+)/i.exec(header);
  if (utf8) {
    try {
      return decodeURIComponent(utf8[1].trim());
    } catch {
      // Mal codificado: se intenta con el nombre simple.
    }
  }
  const plain = /filename="?([^";]+)"?/i.exec(header);
  return plain ? plain[1].trim() : null;
}
