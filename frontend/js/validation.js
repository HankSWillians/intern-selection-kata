/**
 * Reglas del formulario de registro (specs, tabla 3.1). Cada función devuelve
 * el mensaje de error o null. Los textos son los mismos que responde el
 * backend (backend/app/interns/validation.py).
 */
import { CAREERS, OTHER, UNIVERSITIES } from './catalog.js';

export const MAX_CV_MB = 5;

const EMAIL = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;
const CO_MOBILE = /^3\d{9}$/;
const NAME = /^\p{L}[\p{L} '-]*$/u;

export function normalizeSpaces(value) {
  return (value ?? '').trim().replace(/\s+/g, ' ');
}

/** Acepta espacios, guiones y el indicativo +57; deja los 10 dígitos. */
export function normalizePhone(value) {
  const digits = (value ?? '').trim().replace(/[\s\-()]/g, '');
  return digits.startsWith('+57') ? digits.slice(3) : digits;
}

export const rules = {
  fullName(value) {
    const name = normalizeSpaces(value);
    if (!name) return 'Escribe tu nombre completo';
    if (name.length < 3 || name.length > 100) return 'El nombre debe tener entre 3 y 100 caracteres';
    if (!NAME.test(name)) return 'El nombre solo puede tener letras';
    return null;
  },
  email(value) {
    const email = (value ?? '').trim();
    if (!email) return 'Escribe tu correo';
    if (email.length > 254 || !EMAIL.test(email)) return 'Escribe un correo válido';
    return null;
  },
  phone(value) {
    if (!(value ?? '').trim()) return 'Escribe tu celular';
    if (!CO_MOBILE.test(normalizePhone(value))) {
      return 'Escribe un celular colombiano de 10 dígitos que empiece por 3';
    }
    return null;
  },
  university(value) {
    return UNIVERSITIES.includes(value) ? null : 'Elige tu universidad';
  },
  universityOther(value, form) {
    return otherRule(form.university, value, 'Escribe el nombre de tu universidad');
  },
  career(value) {
    return CAREERS.includes(value) ? null : 'Elige tu carrera';
  },
  careerOther(value, form) {
    return otherRule(form.career, value, 'Escribe el nombre de tu carrera');
  },
  semester(value) {
    if (value === '' || value == null) return 'Elige tu semestre';
    const semester = Number(value);
    if (!Number.isInteger(semester) || semester < 1 || semester > 12) {
      return 'El semestre debe estar entre 1 y 12';
    }
    return null;
  },
  /** RF-02 en el navegador: extensión y tamaño. La firma del PDF la revisa el servidor. */
  cv(file) {
    if (!file) return 'Adjunta tu hoja de vida';
    if (!file.name.toLowerCase().endsWith('.pdf')) return 'Solo se permiten archivos PDF';
    if (file.size > MAX_CV_MB * 1024 * 1024) {
      return `La hoja de vida no puede pesar más de ${MAX_CV_MB} MB`;
    }
    return null;
  },
  dataConsent(checked) {
    return checked ? null : 'Debes aceptar el tratamiento de tus datos personales';
  },
};

function otherRule(selected, written, message) {
  if (selected !== OTHER) return null;
  const text = normalizeSpaces(written);
  return text.length < 3 || text.length > 100 ? message : null;
}
