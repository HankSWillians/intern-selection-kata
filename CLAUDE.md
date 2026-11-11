# Contexto del proyecto: Plataforma Básica de Selección de Practicantes

**Qué es:** reto técnico *Kata Practicing – Challenge 1* del proceso de prácticas de la Vicepresidencia de Tecnología del Banco de Bogotá.
**Entrega y sustentación:** jueves 12 de noviembre de 2026, 10:00 a. m. (hora de Bogotá), virtual, de 5 a 7 minutos. Llegar con el reto desarrollado y el entorno listo.
**Requerimientos:** [`specs/requerimientos.md`](specs/README.md). Seguimiento de los casos de prueba en el documento [Requerimientos](https://claude.ai/artifact/PGKebkBttg4XuL8wnv62Ev).
**Referencia:** se trabaja con las mismas convenciones de Kronos (`gpc-kronos`), adaptadas a un proyecto de una sola persona.

---

## 1. El reto

Herramienta web sencilla con dos partes:

- **Formulario del practicante:** nombre completo, correo, carrera, semestre y hoja de vida en PDF, con validación de campos obligatorios.
- **Panel del analista:** lista de practicantes, detalle de cada uno y botones «Viable» / «No viable».
- **Back-end:** API para guardar, listar y actualizar el estado; base de datos local (SQLite); archivos en una carpeta del servidor.
- **Opcionales:** login del analista y descarga de la hoja de vida.
- **Documentación:** README con instalación, ejecución y capturas.

## 2. Decisiones (10 de noviembre de 2026)

- **Stack igual a Kronos:** Java 21 + Spring Boot 4.1 (Maven) en `backend/`, Angular 22 + TypeScript en `frontend/`, Node.js 24 LTS.
- **Base de datos: SQLite** en vez de MySQL. El reto la sugiere, corre en local sin instalar nada y este equipo no tiene Docker. Esquema con migraciones de Flyway.
- **Archivos:** las hojas de vida van en `backend/var/uploads/` (configurable con `UPLOAD_DIR`), con nombre único generado por el servidor. La BD guarda solo ese nombre. `var/` está ignorado.
- **Repositorio privado** en GitHub, creado y publicado desde GitHub Desktop.
- **Se implementan los dos opcionales** (login y descarga) si los obligatorios ya pasan sus pruebas.

## 3. Pendientes

- [ ] ⚠️ Confirmar con Selección si el reto es este (desarrollo) o una «Kata Tester Junior», como dice el WhatsApp.
- [ ] Estructura base: `backend/` y `frontend/`.
- [ ] RF-01 a RF-12.
- [ ] RF-13 (login) y RF-14 (descarga).
- [ ] Pruebas: CP-01 a CP-16.
- [ ] README final con capturas.
- [ ] Datos de ejemplo para la demo y ensayo de la presentación (≤ 7 min).

## 4. Flujo de git y reglas para agentes

**GitHub Flow**, como en Kronos: `main` siempre funciona. Cada cambio sale de una rama corta desde `main` y entra por Pull Request con **squash**. En un repo privado del plan gratuito GitHub no aplica la protección de ramas, así que la regla se cumple por disciplina.

| Elemento | Formato | Ejemplo |
|---|---|---|
| Rama | `<type>/<short-description>` en inglés, minúsculas, sin tildes | `feat/intern-form`, `fix/cv-size-limit` |
| Título del PR | Conventional Commit en inglés: descripción en minúscula, sin punto final, máximo 72 caracteres | `feat(form): add intern registration form` |
| Descripción del PR, documentación | Español | — |

- Tipos: `feat` `fix` `docs` `style` `refactor` `perf` `test` `build` `ci` `chore` `revert`.
- Scopes sugeridos: `form` `panel` `auth` `api` `db` `ci`.

**Reglas para agentes de IA:**
- No hacer `git commit` ni `git push` sin aprobación explícita de quien lleva la sesión. Tampoco abrir PRs ni cambiar ajustes del repositorio en GitHub.
- Ningún secreto entra al repositorio: las credenciales van en `.env`, que está ignorado. Toda variable nueva se agrega a `.env.example`, vacía si es secreta.
- Ninguna hoja de vida ni base de datos real entra al repositorio: son datos personales.
- No renombrar los jobs `CI Gate` ni `PR Validation`.
- En los workflows, los datos que controla el usuario (título del PR, nombre de rama) pasan por `env:`, nunca con `${{ }}` dentro de `run:`.

**Código:**
- Todo en inglés: paquetes, clases, tablas, columnas, endpoints, componentes y nombres de prueba. Comentarios y textos de la interfaz, en español.
- API bajo el prefijo `/api/v1`. En desarrollo `ng serve` reenvía `/api` al backend con `frontend/proxy.conf.json`.
- El esquema solo cambia con una migración nueva de Flyway (`backend/src/main/resources/db/migration/V<n>__<descripcion>.sql`).
- Las validaciones van en el frontend **y** en el backend (RF-12).
- `mvnw` va con permiso de ejecución en git (`git update-index --chmod=+x backend/mvnw`) y `package-lock.json` siempre se commitea.
