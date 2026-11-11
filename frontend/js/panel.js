/** Lista de practicantes con filtro y decisión por fila (RF-06, RF-08, RF-16). */
import { api } from './api.js';
import { renderNav, requireAuth } from './auth.js';
import { EMPTY_MESSAGES, FILTERS, badge, escapeHtml, formatDate, parseFilter } from './format.js';

if (requireAuth()) {
  renderNav('panel');
  const filter = parseFilter(new URLSearchParams(location.search).get('estado'));
  const $ = (selector) => document.querySelector(selector);
  let toastTimer;

  function show(selector) {
    for (const name of ['[data-loading]', '[data-load-error]', '[data-empty]', '[data-table]']) {
      $(name).hidden = name !== selector;
    }
  }

  function toast(text, kind = 'ok') {
    const box = $('[data-toast]');
    box.textContent = text;
    box.className = `toast toast-${kind}`;
    box.hidden = false;
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => (box.hidden = true), 3000);
  }

  function renderTabs(summary) {
    $('[data-tabs]').innerHTML = FILTERS.map((item) => {
      const href = item.value === 'todos' ? '/panel.html' : `/panel.html?estado=${item.value}`;
      const current = item.value === filter.value;
      const count = summary ? `<span class="count">${summary[item.count]}</span>` : '';
      return `<a class="tab${current ? ' active' : ''}" href="${href}"${current ? ' aria-current="page"' : ''}>${item.label} ${count}</a>`;
    }).join('');
  }

  function renderRows(interns) {
    $('[data-rows]').innerHTML = interns
      .map((intern) => {
        const detail = `/detalle.html?id=${intern.id}&desde=${filter.value}`;
        const name = escapeHtml(intern.fullName);
        return `<tr data-id="${intern.id}">
          <td><a class="name" href="${detail}">${name}</a><span class="email">${escapeHtml(intern.email)}</span></td>
          <td class="hide-sm">${escapeHtml(intern.university)}</td>
          <td class="hide-sm">${escapeHtml(intern.career)}</td>
          <td class="num">${intern.semester}</td>
          <td>${badge(intern.status)}</td>
          <td class="date hide-sm">${formatDate(intern.createdAt)}</td>
          <td class="row-actions">
            <button type="button" class="btn btn-sm btn-viable" data-decide="VIABLE"
              ${intern.status === 'VIABLE' ? 'disabled' : ''} aria-label="Marcar a ${name} como viable">Viable</button>
            <button type="button" class="btn btn-sm btn-not-viable" data-decide="NOT_VIABLE"
              ${intern.status === 'NOT_VIABLE' ? 'disabled' : ''} aria-label="Marcar a ${name} como no viable">No viable</button>
          </td>
        </tr>`;
      })
      .join('');
  }

  async function load() {
    show('[data-loading]');
    try {
      const [interns, summary] = await Promise.all([api.list(filter.status), api.summary()]);
      renderTabs(summary);
      if (interns.length === 0) {
        $('[data-empty]').textContent = EMPTY_MESSAGES[filter.value];
        show('[data-empty]');
      } else {
        renderRows(interns);
        show('[data-table]');
      }
    } catch (error) {
      if (error.status !== 401) show('[data-load-error]');
    }
  }

  // RF-08: decisión desde la fila, sin observación (la observación va en el detalle).
  $('[data-rows]').addEventListener('click', async (event) => {
    const button = event.target.closest('[data-decide]');
    if (!button) return;
    const row = button.closest('tr');
    row.querySelectorAll('[data-decide]').forEach((b) => (b.disabled = true));
    try {
      await api.decide(row.dataset.id, button.dataset.decide);
      toast('Decisión guardada');
      await load();
    } catch (error) {
      if (error.status !== 401) {
        toast('No pudimos guardar la decisión. Intenta de nuevo.', 'error');
        await load();
      }
    }
  });

  $('[data-retry]').addEventListener('click', load);
  renderTabs(null);
  load();
}
