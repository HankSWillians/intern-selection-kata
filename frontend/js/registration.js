/** Formulario público del practicante (RF-01 a RF-05, RF-15). */
import { ApiError, api } from './api.js';
import { renderNav } from './auth.js';
import { CAREERS, OTHER, UNIVERSITIES } from './catalog.js';
import { normalizeSpaces, rules } from './validation.js';

export const SUCCESS_MESSAGE =
  '¡Registro exitoso! Tu información quedó en manos del equipo de selección.';
export const GENERAL_ERROR = 'No pudimos enviar tu registro. Intenta de nuevo en unos minutos.';

/** Orden en pantalla: al enviar con errores, el foco va al primero (RF-03). */
const FIELDS = [
  'fullName', 'email', 'phone', 'university', 'universityOther',
  'career', 'careerOther', 'semester', 'cv', 'dataConsent',
];

const form = document.getElementById('registration-form');
const touched = new Set();

renderNav('registro');
fillSelect('f-university', UNIVERSITIES);
fillSelect('f-career', CAREERS);
fillSelect('f-semester', Array.from({ length: 12 }, (_, i) => String(i + 1)));

function fillSelect(id, options) {
  const select = document.getElementById(id);
  for (const option of options) select.add(new Option(option, option));
}

function input(name) {
  return document.getElementById(`f-${name}`);
}

/** Valores actuales del formulario, como los recibe cada regla. */
function values() {
  return {
    fullName: input('fullName').value,
    email: input('email').value,
    phone: input('phone').value,
    university: input('university').value,
    universityOther: input('universityOther').value,
    career: input('career').value,
    careerOther: input('careerOther').value,
    semester: input('semester').value,
    cv: input('cv').files[0] ?? null,
    dataConsent: input('dataConsent').checked,
  };
}

function showError(name, message) {
  const field = input(name);
  document.getElementById(`e-${name}`).textContent = message ?? '';
  if (message) field.setAttribute('aria-invalid', 'true');
  else field.removeAttribute('aria-invalid');
}

/** Valida un campo y muestra su error si ya se tocó o si se intentó enviar. */
function validateField(name, force = false) {
  const current = values();
  const message = rules[name](current[name], current);
  if (force || touched.has(name)) showError(name, message);
  return message;
}

function toggleOther(list) {
  const visible = input(list).value === OTHER;
  form.querySelector(`[data-other="${list}"]`).hidden = !visible;
  if (!visible) {
    input(`${list}Other`).value = '';
    showError(`${list}Other`, null);
  }
}

// Validación al salir de cada campo (RF-05).
for (const name of FIELDS) {
  const field = input(name);
  field.addEventListener('blur', () => {
    touched.add(name);
    validateField(name);
  });
  const typing = field.tagName === 'INPUT' && ['text', 'email', 'tel'].includes(field.type);
  field.addEventListener(typing ? 'input' : 'change', () => {
    if (touched.has(name)) validateField(name);
  });
}

for (const list of ['university', 'career']) {
  input(list).addEventListener('change', () => {
    touched.add(list);
    validateField(list);
    toggleOther(list);
  });
}

input('cv').addEventListener('change', () => {
  touched.add('cv');
  const file = input('cv').files[0];
  form.querySelector('[data-file-name]').textContent = file ? file.name : 'Ningún archivo elegido';
  validateField('cv');
});

input('dataConsent').addEventListener('change', () => {
  touched.add('dataConsent');
  validateField('dataConsent');
});

function setMessage(selector, text) {
  const element = form.querySelector(selector);
  element.textContent = text ?? '';
  element.hidden = !text;
}

form.addEventListener('submit', async (event) => {
  event.preventDefault();
  setMessage('[data-success]', null);
  setMessage('[data-general-error]', null);

  const invalid = FIELDS.filter((name) => validateField(name, true));
  FIELDS.forEach((name) => touched.add(name));
  if (invalid.length > 0) {
    input(invalid[0]).focus();
    return;
  }

  const current = values();
  const data = new FormData();
  data.append('fullName', normalizeSpaces(current.fullName));
  data.append('email', current.email.trim());
  data.append('phone', current.phone.trim());
  data.append('university', current.university);
  data.append('career', current.career);
  if (current.university === OTHER) data.append('universityOther', normalizeSpaces(current.universityOther));
  if (current.career === OTHER) data.append('careerOther', normalizeSpaces(current.careerOther));
  data.append('semester', current.semester);
  data.append('dataConsent', 'true');
  data.append('cv', current.cv, current.cv.name);

  const submit = form.querySelector('[data-submit]');
  submit.disabled = true;
  submit.textContent = 'Enviando…';
  try {
    await api.register(data);
    form.reset();
    touched.clear();
    FIELDS.forEach((name) => showError(name, null));
    toggleOther('university');
    toggleOther('career');
    form.querySelector('[data-file-name]').textContent = 'Ningún archivo elegido';
    setMessage('[data-success]', SUCCESS_MESSAGE);
    form.querySelector('[data-success]').scrollIntoView({ block: 'center' });
  } catch (error) {
    // 400 y 409 traen los errores por campo; el resto es un error general (RF-05).
    const fieldErrors = error instanceof ApiError ? Object.entries(error.errors) : [];
    const known = fieldErrors.filter(([name]) => FIELDS.includes(name));
    if (known.length > 0) {
      known.forEach(([name, message]) => showError(name, message));
      input(known[0][0]).focus();
    } else {
      setMessage('[data-general-error]', GENERAL_ERROR);
    }
  } finally {
    submit.disabled = false;
    submit.textContent = 'Enviar';
  }
});
