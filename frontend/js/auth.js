/**
 * Sesión del analista (RF-13). El token vive en sessionStorage, así que se
 * borra al cerrar la pestaña. El acceso al storage va en try/catch porque
 * algunos navegadores lo bloquean.
 */
const KEY = 'intern-selection.token';
let memoryToken = null;

export function getToken() {
  try {
    return sessionStorage.getItem(KEY);
  } catch {
    return memoryToken;
  }
}

export function setToken(token) {
  memoryToken = token;
  try {
    if (token) sessionStorage.setItem(KEY, token);
    else sessionStorage.removeItem(KEY);
  } catch {
    // Sin storage la sesión dura mientras la página esté abierta.
  }
}

export function isAuthenticated() {
  return Boolean(getToken());
}

/** Sin sesión, lleva al login y guarda a dónde volver. */
export function requireAuth() {
  if (isAuthenticated()) return true;
  const back = location.pathname + location.search;
  location.replace(`/login.html?volver=${encodeURIComponent(back)}`);
  return false;
}

/** Token vencido o inválido: cierra la sesión y lleva al login con el aviso. */
export function expireSession() {
  setToken(null);
  const back = location.pathname + location.search;
  location.replace(`/login.html?expirada=1&volver=${encodeURIComponent(back)}`);
}

export function logout() {
  setToken(null);
  location.href = '/login.html';
}

/** Solo rutas internas del panel: evita redirigir a otro sitio con ?volver=. */
export function safeReturnUrl(url) {
  return url && /^\/(panel|detalle)\.html/.test(url) ? url : '/panel.html';
}

/** Menú del encabezado según haya sesión o no. */
export function renderNav(current) {
  const nav = document.querySelector('[data-nav]');
  if (!nav) return;
  const link = (href, label, key) =>
    `<a href="${href}"${current === key ? ' aria-current="page"' : ''}>${label}</a>`;
  if (isAuthenticated()) {
    nav.innerHTML = `${link('/panel.html', 'Panel', 'panel')}<button type="button" data-logout>Cerrar sesión</button>`;
    nav.querySelector('[data-logout]').addEventListener('click', logout);
  } else {
    nav.innerHTML = `${link('/', 'Registro', 'registro')}${link('/login.html', 'Soy analista', 'login')}`;
  }
}
