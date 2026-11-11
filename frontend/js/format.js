/** Textos y formatos de presentación compartidos por el panel y el detalle. */

export const STATUS_LABELS = { PENDING: 'Pendiente', VIABLE: 'Viable', NOT_VIABLE: 'No viable' };

/** Pestañas del panel (RF-16): valor en la URL ↔ estado de la API. */
export const FILTERS = [
  { value: 'todos', label: 'Todos', status: null, count: 'total' },
  { value: 'pendientes', label: 'Pendientes', status: 'PENDING', count: 'pending' },
  { value: 'viables', label: 'Viables', status: 'VIABLE', count: 'viable' },
  { value: 'no-viables', label: 'No viables', status: 'NOT_VIABLE', count: 'notViable' },
];

export function parseFilter(value) {
  return FILTERS.find((f) => f.value === value) ?? FILTERS[0];
}

export const EMPTY_MESSAGES = {
  todos: 'No hay practicantes registrados',
  pendientes: 'No hay practicantes pendientes',
  viables: 'No hay practicantes viables',
  'no-viables': 'No hay practicantes no viables',
};

const DATE_TIME = new Intl.DateTimeFormat('es-CO', {
  dateStyle: 'medium',
  timeStyle: 'short',
  timeZone: 'America/Bogota',
});
const DATE = new Intl.DateTimeFormat('es-CO', { dateStyle: 'medium', timeZone: 'America/Bogota' });

export const formatDateTime = (value) => (value ? DATE_TIME.format(new Date(value)) : '—');
export const formatDate = (value) => (value ? DATE.format(new Date(value)) : '—');

/** +573001234567 → 300 123 4567 */
export function formatPhone(value) {
  const digits = (value ?? '').replace(/^\+57/, '');
  return /^\d{10}$/.test(digits) ? `${digits.slice(0, 3)} ${digits.slice(3, 6)} ${digits.slice(6)}` : value ?? '';
}

/** Escapa texto antes de ponerlo en HTML: los datos vienen del formulario público. */
export function escapeHtml(value) {
  return String(value ?? '').replace(
    /[&<>"']/g,
    (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c],
  );
}

export function badge(status) {
  return `<span class="badge badge-${status.toLowerCase()}">${STATUS_LABELS[status]}</span>`;
}
