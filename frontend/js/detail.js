/** Detalle, decisión con observación y descarga (RF-07, RF-08, RF-14, RF-17, RF-18). */
import { ApiError, api } from './api.js';
import { renderNav, requireAuth } from './auth.js';
import { badge, formatDateTime, formatPhone, parseFilter } from './format.js';

if (requireAuth()) {
  renderNav('panel');
  const params = new URLSearchParams(location.search);
  const id = Number(params.get('id'));
  const from = parseFilter(params.get('desde'));
  const $ = (selector) => document.querySelector(selector);
  const note = $('#note');
  let intern = null;

  $('[data-back]').href = from.value === 'todos' ? '/panel.html' : `/panel.html?estado=${from.value}`;

  function feedback(text, kind = 'ok') {
    const box = $('[data-feedback]');
    box.textContent = text ?? '';
    box.classList.toggle('ok', kind === 'ok');
  }

  function render() {
    $('[data-name]').textContent = intern.fullName;
    document.title = `${intern.fullName} · Selección de Practicantes`;
    $('[data-created]').textContent = `Registrado el ${formatDateTime(intern.createdAt)}`;
    $('[data-badge]').innerHTML = badge(intern.status);
    const email = $('[data-email]');
    email.textContent = intern.email;
    email.href = `mailto:${intern.email}`;
    $('[data-phone]').textContent = formatPhone(intern.phone);
    $('[data-university]').textContent = intern.university;
    $('[data-career]').textContent = intern.career;
    $('[data-semester]').textContent = intern.semester;
    $('[data-consent]').textContent = `Aceptado el ${formatDateTime(intern.dataConsentAt)}`;
    $('[data-reviewed]').textContent = intern.reviewedAt
      ? `Última decisión: ${formatDateTime(intern.reviewedAt)}`
      : 'Aún no tiene decisión.';
    note.value = intern.reviewNote ?? '';
    $('[data-note-count]').textContent = note.value.length;
    for (const button of document.querySelectorAll('[data-decide]')) {
      const current = button.dataset.decide === intern.status;
      button.disabled = current;
      button.classList.toggle('current', current);
      button.setAttribute('aria-pressed', String(current));
    }
  }

  async function load() {
    try {
      intern = await api.get(id);
      $('[data-loading]').hidden = true;
      $('[data-detail]').hidden = false;
      render();
    } catch (error) {
      if (error.status === 401) return;
      $('[data-loading]').hidden = true;
      const box = $('[data-load-error]');
      box.textContent = error instanceof ApiError && error.status === 404
        ? 'Este practicante no existe.'
        : 'No pudimos cargar el practicante.';
      box.hidden = false;
    }
  }

  note.addEventListener('input', () => {
    $('[data-note-count]').textContent = note.value.length;
  });

  for (const button of document.querySelectorAll('[data-decide]')) {
    button.addEventListener('click', async () => {
      const buttons = document.querySelectorAll('[data-decide]');
      buttons.forEach((b) => (b.disabled = true));
      const label = button.textContent;
      button.textContent = 'Guardando…';
      feedback(null);
      try {
        intern = await api.decide(id, button.dataset.decide, note.value.trim());
        button.textContent = label;
        render();
        feedback('Decisión guardada');
      } catch (error) {
        button.textContent = label;
        if (error.status === 401) return;
        render();
        feedback(error.errors?.note ?? 'No pudimos guardar la decisión. Intenta de nuevo.', 'error');
      }
    });
  }

  $('[data-download]').addEventListener('click', async () => {
    const button = $('[data-download]');
    button.disabled = true;
    button.textContent = 'Descargando…';
    try {
      await api.downloadCv(id);
    } catch (error) {
      if (error.status !== 401) feedback('No pudimos descargar la hoja de vida.', 'error');
    } finally {
      button.disabled = false;
      button.textContent = 'Descargar hoja de vida';
    }
  });

  load();
}
