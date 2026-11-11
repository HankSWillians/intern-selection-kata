# Contexto del proyecto: Plataforma Básica de Selección de Practicantes

**Qué es:** reto técnico *Kata Practicing – Challenge 1* del proceso de prácticas de la Vicepresidencia de Tecnología del Banco de Bogotá.
**Entrega:** miércoles 11 de noviembre de 2026, 11:00 a. m. (hora de Bogotá), con el repositorio público.
**Sustentación:** jueves 12 de noviembre de 2026, 10:00 a. m., virtual, de 5 a 7 minutos. Llegar con el reto desarrollado y el entorno listo.
**Requerimientos:** [`specs/requerimientos.md`](specs/README.md). Seguimiento de los casos de prueba en el documento [Requerimientos](https://claude.ai/artifact/PGKebkBttg4XuL8wnv62Ev).
**Referencia:** se trabaja con las mismas convenciones de repositorio de Kronos (`gpc-kronos`), adaptadas a un proyecto de una sola persona. El stack **no** es el de Kronos.

---

## 1. El reto

Herramienta web sencilla con dos partes (documento del reto):

- **Formulario del practicante** con HTML y CSS, y validación de campos obligatorios con JavaScript: nombre completo, correo, carrera, semestre y hoja de vida en PDF.
- **Página de listado para los analistas** con botones «Viable» y «No viable», y la información de cada practicante.
- **Back-end:** API para guardar, listar y actualizar el estado; base de datos local (SQLite); archivos en una carpeta del servidor. El reto sugiere Node.js (Express), Python (Flask) o Java (Spring Boot).
- **Opcionales:** login del analista y descarga de la hoja de vida.
- **Documentación:** README con instalación, ejecución y capturas.

## 2. Decisiones

**10 de noviembre de 2026:**
- **Base de datos: SQLite.** El reto la sugiere y corre en local sin instalar nada.
- **Archivos:** las hojas de vida van en `backend/var/uploads/` (`UPLOAD_DIR`), con nombre generado por el servidor. La base guarda solo ese nombre. `var/` está ignorado.
- **Se implementan los dos opcionales** (login y descarga).

**11 de noviembre de 2026** (detalle en la sección 13 de la spec):
- **Stack:** Python 3.12 + **Flask 3.1** en `backend/`; **HTML, CSS y JavaScript puro** en `frontend/`, sin framework ni compilación. Flask sirve las páginas y la API en el mismo origen. Reemplaza a Spring Boot + Angular, que nunca llegaron a `main`.
- **Datos:** `sqlite3` de la biblioteca estándar con SQL directo; migraciones numeradas propias en `backend/migrations/` (`NNN_descripcion.sql`), aplicadas al arrancar y registradas en `schema_migrations`.
- **Login con JWT** (PyJWT). El token va en `sessionStorage` y en el encabezado `Authorization: Bearer`. La contraseña del analista se guarda en memoria con hash de Werkzeug.
- **Campos adicionales al reto:** universidad, celular y casilla de tratamiento de datos (Ley 1581). Carrera y universidad con lista + «Otra».
- **Decisión del analista:** botones en cada fila de la lista y en el detalle; cambia entre Viable y No viable, nunca vuelve a Pendiente; observación opcional (solo desde el detalle).
- **Panel:** filtro por estado con conteos; sin búsqueda.
- **Diseño:** paleta inspirada en el Banco de Bogotá, **sin su logo ni su nombre** en la aplicación.
- **Pruebas:** pytest para la API; Playwright (Python) para el navegador, si da el tiempo antes de la entrega.
- **Datos de demostración:** `DEMO_DATA=true` carga 4 practicantes ficticios si la base está vacía.
- **Alcance:** el correo no especifica otro reto; la base es el documento del reto (desarrollo).
- **Entrega:** repositorio público. Tres PR: base, API y frontend (con README final y capturas).

## 3. Pendientes

- [x] Specs completas (`specs/requerimientos.md`).
- [x] PR 1, base: Flask, migraciones, frontend estático y CI (`feat/project-scaffold`).
- [x] PR 2, API: RF-09 a RF-19 en el backend con pytest (`feat/backend-api`).
- [x] PR 3, frontend: registro, login, panel y detalle; Playwright; README final y capturas (`feat/frontend`).
- [ ] Repositorio público y envío antes de las 11:00.
- [ ] Ensayo de la presentación (≤ 7 min).

## 4. Flujo de git y reglas para agentes

**GitHub Flow**, como en Kronos: `main` siempre funciona. Cada cambio sale de una rama corta desde `main` y entra por Pull Request con **squash**.

| Elemento | Formato | Ejemplo |
|---|---|---|
| Rama | `<type>/<short-description>` en inglés, minúsculas, sin tildes | `feat/intern-form`, `fix/cv-size-limit` |
| Título del PR | Conventional Commit en inglés: descripción en minúscula, sin punto final, máximo 72 caracteres | `feat(api): add interns endpoints` |
| Descripción del PR, documentación | Español | — |

- Tipos: `feat` `fix` `docs` `style` `refactor` `perf` `test` `build` `ci` `chore` `revert`.
- Scopes sugeridos: `api` `web` `auth` `db` `ci`.

**Reglas para agentes de IA:**
- No hacer `git commit` ni `git push` sin aprobación explícita de quien lleva la sesión. Tampoco abrir PRs ni cambiar ajustes del repositorio en GitHub.
- Ningún secreto entra al repositorio: las credenciales van en `.env`, que está ignorado. Toda variable nueva se agrega a `.env.example`, vacía si es secreta.
- Ninguna hoja de vida ni base de datos real entra al repositorio: son datos personales. El repositorio es público.
- No renombrar los jobs `CI Gate` ni `PR Validation`.
- En los workflows, los datos que controla el usuario (título del PR, nombre de rama) pasan por `env:`, nunca con `${{ }}` dentro de `run:`.

**Código:**
- Nombres en inglés: módulos, funciones, tablas, columnas, endpoints y pruebas. Comentarios y textos de la interfaz, en español.
- API bajo el prefijo `/api/v1`. Errores en formato Problem Details con `errors` por campo (RNF-12).
- El esquema solo cambia con una migración nueva en `backend/migrations/`. Nunca se edita una ya integrada en `main`.
- Las validaciones van en el frontend **y** en el backend (RF-12), con los mismos mensajes de la spec.
- Las listas de universidades y carreras están en `backend/app/catalog.py` y `frontend/js/catalog.js`: si cambia una, se cambia la otra.
- Las pruebas llevan en el nombre o en el docstring el caso de la spec que cubren (`CP-xx`).
- Ejecutar: `python -m flask --app app run` desde `backend/`. Probar: `python -m pytest` desde `backend/` (las pruebas de `tests/e2e/` necesitan `python -m playwright install chromium`).
- Las ayudas de las pruebas están en `tests/helpers.py`, no en `conftest.py`: hay dos `conftest.py` y un `from conftest import` choca entre ellos.
- Frontend: módulos ES (`<script type="module">`), sin compilación. Todo dato que viene del formulario se escapa con `escapeHtml` antes de ponerlo en el HTML.
