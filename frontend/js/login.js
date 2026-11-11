/** Ingreso del analista (RF-13). */
import { ApiError, api } from './api.js';
import { isAuthenticated, renderNav, safeReturnUrl, setToken } from './auth.js';

export const INVALID_CREDENTIALS = 'Usuario o contraseña incorrectos';

const params = new URLSearchParams(location.search);
const back = safeReturnUrl(params.get('volver'));

if (isAuthenticated() && !params.has('expirada')) {
  location.replace(back);
}

renderNav('login');
const form = document.getElementById('login-form');
const expired = form.querySelector('[data-expired]');
const errorBox = form.querySelector('[data-error]');
expired.hidden = !params.has('expirada');

function showError(message) {
  errorBox.textContent = message ?? '';
  errorBox.hidden = !message;
  if (message) expired.hidden = true;
}

form.addEventListener('submit', async (event) => {
  event.preventDefault();
  const username = form.username.value.trim();
  const password = form.password.value;
  if (!username || !password) {
    showError(INVALID_CREDENTIALS);
    return;
  }
  const submit = form.querySelector('[data-submit]');
  submit.disabled = true;
  submit.textContent = 'Ingresando…';
  try {
    const { token } = await api.login(username, password);
    setToken(token);
    location.href = back;
  } catch (error) {
    showError(
      error instanceof ApiError && error.status === 401
        ? INVALID_CREDENTIALS
        : 'No pudimos conectar con el servidor. Intenta de nuevo.',
    );
    submit.disabled = false;
    submit.textContent = 'Ingresar';
  }
});
