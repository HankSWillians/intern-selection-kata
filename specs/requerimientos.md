# Requerimientos – Plataforma Básica de Selección de Practicantes

**Última actualización:** 11 de noviembre de 2026 (cambio de stack a Flask y HTML, CSS y JS)
**Estado:** definida, sin dudas abiertas. Las decisiones están registradas en la sección 13.

---

## 1. Contexto y alcance

La plataforma permite que los practicantes registren sus datos y su hoja de vida en PDF, y que un analista de selección los revise y los marque como **Viable** o **No viable**. Corre en local, sin despliegue en la nube. Corresponde al reto *Kata Practicing – Challenge 1* de la Vicepresidencia de Tecnología. Se entrega el 11 de noviembre de 2026 a las 11:00 a. m. y se sustenta en 5 a 7 minutos el 12 de noviembre a las 10:00 a. m.

**Supuestos**

- Hay un único analista, con credenciales fijas configuradas en el servidor.
- Todo practicante nuevo queda en estado **Pendiente** hasta que el analista decida.
- Un correo electrónico solo puede registrarse una vez.

**Alcance confirmado** (11 de noviembre de 2026): el mensaje de Selección menciona una «Kata Tester Junior», pero el correo no especifica otro reto, así que la base es el documento del reto (desarrollo).

## 2. Roles y permisos

| Acción | Practicante (sin sesión) | Analista (con sesión) |
|---|---|---|
| Registrarse con el formulario | ✅ | ✅ |
| Ver la lista de practicantes y filtrarla | — | ✅ |
| Ver el detalle de un practicante | — | ✅ |
| Marcar Viable o No viable, con observación | — | ✅ |
| Descargar la hoja de vida | — | ✅ |

El practicante no tiene cuenta: después de enviar el formulario no puede consultar ni editar su registro.

## 3. Registro del practicante

### 3.1 Campos

- **RF-01.** El formulario pide estos datos. **Todos son obligatorios.** Las validaciones se hacen en el navegador (RF-03 y RF-04) y se repiten en el servidor (RF-12) con los mismos mensajes.

| Campo | Campo en la API | Regla | Mensaje de error |
|---|---|---|---|
| Nombre completo | `fullName` | 3 a 100 caracteres. Letras (con tildes y ñ), espacios, apóstrofo y guion. Se recortan los espacios de los extremos y se unen los repetidos | «Escribe tu nombre completo» · «El nombre debe tener entre 3 y 100 caracteres» · «El nombre solo puede tener letras» |
| Correo electrónico | `email` | Formato válido, máximo 254 caracteres. Se guarda en minúsculas. Único (RF-12) | «Escribe tu correo» · «Escribe un correo válido» · «Ya existe un registro con este correo» |
| Celular | `phone` | Celular colombiano: 10 dígitos que empiezan por 3. Se aceptan espacios y guiones al escribir; se guarda como `+573001234567` | «Escribe tu celular» · «Escribe un celular colombiano de 10 dígitos que empiece por 3» |
| Universidad | `university` | Se elige de la lista (sección 3.2) o «Otra». Si es «Otra», se escribe el nombre: 3 a 100 caracteres | «Elige tu universidad» · «Escribe el nombre de tu universidad» |
| Carrera universitaria | `career` | Se elige de la lista (sección 3.2) o «Otra». Si es «Otra», se escribe el nombre: 3 a 100 caracteres | «Elige tu carrera» · «Escribe el nombre de tu carrera» |
| Semestre actual | `semester` | Entero de 1 a 12. En el formulario es una lista desplegable | «Elige tu semestre» · «El semestre debe estar entre 1 y 12» |
| Hoja de vida | `cv` | Archivo PDF de máximo 5 MB (RF-02) | «Adjunta tu hoja de vida» · «Solo se permiten archivos PDF» · «La hoja de vida no puede pesar más de 5 MB» |
| Tratamiento de datos | `dataConsent` | Casilla obligatoria (RF-15) | «Debes aceptar el tratamiento de tus datos personales» |

- Cuando se elige «Otra», el servidor guarda el texto escrito, no la palabra «Otra».

### 3.2 Listas

Viven en el código (`frontend/js/catalog.js` y `backend/app/catalog.py` tienen los mismos valores), no en la base de datos. Cambiarlas es un cambio de código.

**Universidades:** Universidad Nacional de Colombia, Universidad de los Andes, Pontificia Universidad Javeriana, Universidad del Rosario, Universidad Distrital Francisco José de Caldas, Universidad El Bosque, Universidad de La Sabana, Escuela Colombiana de Ingeniería Julio Garavito, Universidad Externado de Colombia, Universidad Militar Nueva Granada, Universidad Piloto de Colombia, Universidad Católica de Colombia, Universidad Sergio Arboleda, Universidad EAN, Universidad Santo Tomás, Fundación Universitaria Konrad Lorenz, Politécnico Grancolombiano, Otra.

**Carreras:** Ingeniería de Sistemas, Ingeniería de Software, Ingeniería Informática, Ingeniería de Sistemas y Computación, Ingeniería Electrónica, Ingeniería de Telecomunicaciones, Ingeniería Industrial, Ingeniería Matemática, Ciencia de Datos, Matemáticas, Estadística, Tecnología en Desarrollo de Software, Otra.

### 3.3 Hoja de vida

- **RF-02.** El practicante adjunta su hoja de vida. El archivo se acepta solo si cumple las tres condiciones:
  1. Su extensión es `.pdf`.
  2. Su contenido empieza con la firma de un PDF (`%PDF-`). Así se rechaza un archivo de otro tipo renombrado a `.pdf`.
  3. Pesa como máximo **5 MB** (configurable con `MAX_CV_SIZE_MB`).
- El navegador revisa la extensión y el tamaño antes de enviar; el servidor revisa las tres condiciones.
- El servidor guarda el archivo en la carpeta de archivos con un **nombre generado** (UUID + `.pdf`). El nombre original no se usa para guardar, para evitar rutas maliciosas y choques.

### 3.4 Validación y envío

- **RF-03.** Ningún campo puede quedar vacío. El formulario no se envía mientras haya errores.
- **RF-04.** Además de lo obligatorio, se validan los formatos de la tabla 3.1: correo, celular, semestre de 1 a 12 y PDF de máximo 5 MB.
- Cada campo muestra su error debajo, al salir del campo y al intentar enviar. Al intentar enviar con errores, el foco va al primer campo con error.
- **RF-05.** Mensajes del envío:
  - Mientras se envía, el botón «Enviar» se desactiva y muestra «Enviando…», para evitar dobles registros.
  - **Éxito:** «¡Registro exitoso! Tu información quedó en manos del equipo de selección.» El formulario se limpia.
  - **Correo duplicado** (409): el error aparece debajo del campo de correo y los demás datos se conservan.
  - **Otro error del servidor o sin conexión:** «No pudimos enviar tu registro. Intenta de nuevo en unos minutos.» Los datos se conservan.

### 3.5 Tratamiento de datos personales

- **RF-15.** El formulario tiene una **casilla obligatoria** de aceptación del tratamiento de datos personales, con el texto: «Autorizo el tratamiento de mis datos personales para este proceso de selección, conforme a la Ley 1581 de 2012.»
  - El servidor guarda la **fecha y hora de la aceptación** como evidencia.
  - Sin la casilla marcada, el servidor rechaza el registro (400).

## 4. Panel del analista

### 4.1 Lista

- **RF-06.** El panel (`/panel.html`) muestra una tabla con los practicantes registrados: nombre, universidad, carrera, semestre, estado, fecha de registro y los botones de decisión (RF-08).
  - Orden: los más recientes primero.
  - Cada estado tiene su color y su texto (RNF-05): Pendiente, Viable, No viable. El color nunca es la única señal.
  - Sin registros: «No hay practicantes registrados».
- **RF-16.** **Filtro por estado.** Encima de la tabla hay pestañas «Todos», «Pendientes», «Viables» y «No viables», cada una con su cantidad.
  - El filtro elegido se refleja en la URL (`/panel.html?estado=pendientes`), para que se conserve al recargar.
  - Una pestaña sin resultados dice, por ejemplo, «No hay practicantes viables».

### 4.2 Detalle

- **RF-07.** Al hacer clic en el nombre se abre el detalle del practicante (`/detalle.html?id={id}`), con todos sus datos: nombre, correo, celular, universidad, carrera, semestre, fecha de registro, fecha de aceptación del tratamiento de datos, estado, observación y fecha de la última decisión.
  - El detalle tiene un enlace para volver a la lista con el mismo filtro.

### 4.3 Decisión

- **RF-08.** Cada fila de la lista y el detalle tienen los botones **«Viable»** y **«No viable»**, como pide el reto («página de listado para los analistas con botones de "Viable" y "No viable"»). Al pulsar uno, el estado cambia, se guarda y se ve de inmediato, sin recargar.
  - Desde la lista se decide sin observación; para escribir una, se usa el detalle (RF-17).
  - El botón del estado actual se muestra activo y no se puede pulsar.
  - Tras guardar aparece «Decisión guardada»; si falla, «No pudimos guardar la decisión. Intenta de nuevo.» y el estado no cambia.
- **RF-17.** **Observación.** Junto a los botones hay un campo de texto **opcional**, de máximo 500 caracteres, que se guarda con la decisión.
  - Si se cambia la decisión, la observación nueva reemplaza a la anterior. Si se deja vacía, se borra la anterior.
- **RF-18.** **Cambios de estado permitidos:**

| Desde | Hacia | Permitido |
|---|---|---|
| Pendiente | Viable o No viable | ✅ |
| Viable | No viable | ✅ |
| No viable | Viable | ✅ |
| Viable o No viable | Pendiente | ❌ (400) |

  - Cada decisión guarda su fecha y hora (`reviewedAt`). No se lleva historial de decisiones anteriores (sección 12).

### 4.4 Hoja de vida

- **RF-14.** El detalle tiene el botón «Descargar hoja de vida». Descarga el PDF original con el nombre `CV - <nombre completo>.pdf`.
  - Como la descarga exige sesión (RF-13), el frontend pide el archivo con el token y luego dispara la descarga; un enlace directo no llevaría el token.

## 5. Acceso del analista

- **RF-13.** Solo el analista con sesión puede ver el panel y llamar a las rutas de consulta, decisión y descarga. El formulario de registro es público.
- **Credenciales:** usuario y contraseña en las variables de entorno `ANALYST_USERNAME` y `ANALYST_PASSWORD`. Al arrancar, el backend guarda la contraseña en memoria con hash BCrypt y no vuelve a usar el texto plano. Si falta la contraseña o `JWT_SECRET` tiene menos de 32 caracteres, el backend no arranca.
- **Inicio de sesión** (`/login.html`): `POST /api/v1/auth/login` con usuario y contraseña.
  - Correcto: devuelve un **JWT** firmado con `JWT_SECRET` (HS256), que vence a las **8 horas**.
  - Incorrecto: 401 y el mensaje «Usuario o contraseña incorrectos», sin decir cuál de los dos falló.
- **Sesión en el frontend:** el token se guarda en `sessionStorage` (se borra al cerrar la pestaña) y viaja en el encabezado `Authorization: Bearer <token>`.
  - Si una respuesta llega con 401 (token vencido o inválido), se borra el token y se redirige a `/login.html` con el mensaje «Tu sesión expiró. Vuelve a iniciar sesión.»
  - Entrar a `/panel.html` o `/detalle.html` sin sesión redirige a `/login.html`; tras ingresar, vuelve a la página que se pidió.
  - El panel tiene un botón «Cerrar sesión».

## 6. Requerimientos no funcionales

| ID | Categoría | Requerimiento |
|---|---|---|
| RNF-01 | Ejecución | Funciona en local; no requiere nube ni Docker |
| RNF-02 | Persistencia | Base de datos SQLite en un único archivo (`DB_PATH`); se crea sola al arrancar y se aplican las migraciones numeradas de `backend/migrations/` (`001_…sql`), cada una una sola vez |
| RNF-03 | Archivos | Las hojas de vida se guardan en `UPLOAD_DIR` con nombre generado (RF-02); la base guarda solo ese nombre |
| RNF-04 | Tecnología | Frontend en HTML, CSS y JavaScript puro, sin framework, como sugiere el reto; backend en Python 3.12 con Flask 3.1, que también sirve el frontend; solo herramientas gratuitas |
| RNF-05 | Usabilidad | Interfaz en español. Estados con color **y** texto. Contraste de texto de al menos 4,5:1. Cada campo con su etiqueta visible |
| RNF-06 | Seguridad | Solo PDF reales (RF-02); nombres de archivo generados; credenciales y secretos solo en `.env`; las hojas de vida y los datos solo se entregan con sesión |
| RNF-07 | Mantenibilidad | Código por capas (rutas, servicio, repositorio) y versionado con GitHub Flow |
| RNF-08 | Documentación | README con requisitos, instalación, ejecución, credenciales de prueba y capturas de pantalla |
| RNF-09 | Rendimiento | Las respuestas de la API tardan menos de 1 segundo con 100 registros en local |
| RNF-10 | Diseño | Paleta inspirada en el Banco de Bogotá (azul corporativo como color principal), **sin logo ni nombre del banco** dentro de la aplicación. Los valores de color se toman del sitio público del banco al implementar el diseño |
| RNF-11 | Adaptable | Formulario y panel usables desde 375 px de ancho (celular) |
| RNF-12 | Errores | Las respuestas de error usan el formato *Problem Details* (RFC 9457), con los errores por campo en `errors` (sección 8) |
| RNF-13 | Pruebas | Pruebas automatizadas de la API con pytest y del navegador con Playwright (Python). La sección 10 dice qué caso cubre cada una |

## 7. Modelo de datos

Una sola tabla. Los nombres en el código van en inglés.

**Tabla `interns`**

| Columna | Tipo | Reglas |
|---|---|---|
| `id` | INTEGER | Llave primaria, autoincremental |
| `full_name` | TEXT | Obligatorio, 3 a 100 caracteres |
| `email` | TEXT | Obligatorio, en minúsculas, **único** |
| `phone` | TEXT | Obligatorio, formato `+57XXXXXXXXXX` |
| `university` | TEXT | Obligatorio |
| `career` | TEXT | Obligatorio |
| `semester` | INTEGER | Obligatorio, 1 a 12 |
| `cv_file_name` | TEXT | Nombre generado del PDF |
| `cv_original_name` | TEXT | Nombre original del archivo, solo informativo |
| `data_consent_at` | TEXT | Fecha y hora de aceptación del tratamiento de datos (ISO 8601) |
| `status` | TEXT | `PENDING`, `VIABLE` o `NOT_VIABLE`; por defecto `PENDING` |
| `review_note` | TEXT | Observación de la última decisión; puede ser nula |
| `reviewed_at` | TEXT | Fecha y hora de la última decisión; nula mientras esté pendiente |
| `created_at` | TEXT | Fecha y hora de registro (ISO 8601) |

## 8. Contrato de la API

Prefijo `/api/v1`. JSON en todas las rutas salvo el registro (`multipart/form-data`) y la descarga (PDF).

| Método | Ruta | Sesión | Uso | Respuestas | RF |
|---|---|---|---|---|---|
| POST | `/interns` | No | Registrar practicante (campos de 3.1 + `cv`) | 201; 400 validación; 409 correo duplicado; 413 archivo muy grande | RF-09, RF-12, RF-15 |
| GET | `/interns?status=PENDING` | Sí | Listar practicantes; `status` es opcional | 200; 401 | RF-10, RF-16 |
| GET | `/interns/summary` | Sí | Cantidad por estado, para las pestañas | 200; 401 | RF-16 |
| GET | `/interns/{id}` | Sí | Detalle | 200; 401; 404 | RF-07 |
| PATCH | `/interns/{id}/status` | Sí | Decidir: `{"status":"VIABLE","note":"..."}` | 200; 400 estado inválido o `PENDING`; 401; 404 | RF-11, RF-17, RF-18 |
| GET | `/interns/{id}/cv` | Sí | Descargar el PDF | 200; 401; 404 | RF-14 |
| POST | `/auth/login` | No | Iniciar sesión: `{"username":"...","password":"..."}` | 200 `{"token":"...","expiresAt":"..."}`; 401 | RF-13 |

**Ejemplo de detalle** (`GET /interns/1`):

```json
{
  "id": 1,
  "fullName": "Laura Gómez",
  "email": "laura@correo.com",
  "phone": "+573001234567",
  "university": "Universidad Nacional de Colombia",
  "career": "Ingeniería de Sistemas",
  "semester": 8,
  "status": "PENDING",
  "reviewNote": null,
  "reviewedAt": null,
  "dataConsentAt": "2026-11-11T09:30:00-05:00",
  "createdAt": "2026-11-11T09:30:00-05:00"
}
```

**Ejemplo de error** (RNF-12):

```json
{
  "type": "about:blank",
  "title": "Datos inválidos",
  "status": 400,
  "detail": "Revisa los campos marcados.",
  "errors": {
    "email": "Escribe un correo válido",
    "semester": "El semestre debe estar entre 1 y 12"
  }
}
```

## 9. Historias de usuario y criterios de aceptación

**HU-01 – Registro del practicante** (RF-01 a RF-05, RF-09, RF-12, RF-15)
Como practicante, quiero registrar mis datos y mi hoja de vida para postularme a la práctica.

```gherkin
Escenario: Registro exitoso
  Dado que estoy en el formulario de registro
  Cuando diligencio todos los campos con datos válidos, adjunto un PDF y acepto el tratamiento de datos
  Y presiono "Enviar"
  Entonces veo el mensaje "¡Registro exitoso! Tu información quedó en manos del equipo de selección."
  Y el formulario queda limpio
  Y mi registro queda guardado con estado "Pendiente"

Escenario: Campo obligatorio vacío
  Cuando dejo el nombre vacío y presiono "Enviar"
  Entonces veo "Escribe tu nombre completo" debajo del nombre
  Y el formulario no se envía

Escenario: Archivo que no es PDF
  Cuando adjunto un archivo .docx
  Entonces veo "Solo se permiten archivos PDF"

Escenario: Universidad que no está en la lista
  Cuando elijo "Otra" en universidad y escribo "Universidad de Cundinamarca"
  Y envío el formulario
  Entonces mi registro guarda "Universidad de Cundinamarca" como universidad

Escenario: Sin aceptar el tratamiento de datos
  Cuando no marco la casilla de tratamiento de datos y presiono "Enviar"
  Entonces veo "Debes aceptar el tratamiento de tus datos personales"
```

**HU-02 – Lista de practicantes** (RF-06, RF-10, RF-16)
Como analista, quiero ver y filtrar la lista de practicantes para saber a quién revisar.

```gherkin
Escenario: Ver lista
  Dado que existen practicantes registrados
  Cuando ingreso al panel
  Entonces veo una fila por practicante, los más recientes primero

Escenario: Filtrar pendientes
  Dado que hay 2 practicantes pendientes y 1 viable
  Cuando elijo la pestaña "Pendientes"
  Entonces veo solo los 2 pendientes
  Y la pestaña muestra la cantidad 2

Escenario: Lista vacía
  Dado que no hay registros
  Cuando ingreso al panel
  Entonces veo "No hay practicantes registrados"
```

**HU-03 – Detalle y decisión** (RF-07, RF-08, RF-11, RF-17, RF-18)
Como analista, quiero ver la información de un practicante y marcarlo como Viable o No viable, con una observación si hace falta.

```gherkin
Escenario: Marcar como viable
  Dado que veo el detalle de un practicante en estado "Pendiente"
  Cuando presiono "Viable"
  Entonces veo "Decisión guardada"
  Y su estado cambia a "Viable" en el detalle y en la lista
  Y el cambio se conserva al recargar la página

Escenario: Corregir la decisión con una observación
  Dado que un practicante está en "Viable"
  Cuando escribo "No cumple el semestre mínimo" y presiono "No viable"
  Entonces su estado cambia a "No viable"
  Y el detalle muestra la observación y la fecha de la decisión
```

**HU-04 – Acceso restringido** (RF-13)
Como analista, quiero iniciar sesión para que solo yo vea el panel.

```gherkin
Escenario: Acceso sin sesión
  Dado que no he iniciado sesión
  Cuando intento abrir el panel
  Entonces soy redirigido al login
  Y al ingresar vuelvo al panel

Escenario: Credenciales inválidas
  Cuando ingreso una contraseña incorrecta
  Entonces veo "Usuario o contraseña incorrectos"

Escenario: Sesión vencida
  Dado que mi token venció
  Cuando hago cualquier acción en el panel
  Entonces soy redirigido al login con "Tu sesión expiró. Vuelve a iniciar sesión."
```

**HU-05 – Descarga de hoja de vida** (RF-14)
Como analista, quiero descargar la hoja de vida para revisarla en detalle.

```gherkin
Escenario: Descargar PDF
  Dado que veo el detalle de "Laura Gómez"
  Cuando presiono "Descargar hoja de vida"
  Entonces se descarga "CV - Laura Gómez.pdf", idéntico al que ella subió
```

## 10. Casos de prueba y trazabilidad

La columna **Automatizada** dice dónde vive la prueba: **API** (pytest con el cliente de pruebas de Flask, sin pasar por el formulario, para comprobar que el servidor valida por su cuenta) o **E2E** (Playwright en el navegador).

| ID | Caso | Datos de entrada | Resultado esperado | RF | Automatizada |
|---|---|---|---|---|---|
| CP-01 | Registro exitoso | Datos válidos + PDF de 200 KB + casilla marcada | 201; queda en `PENDING`; el PDF existe en `UPLOAD_DIR` | RF-01, RF-02, RF-09 | API |
| CP-02 | Nombre vacío | Nombre en blanco | «Escribe tu nombre completo»; no se envía | RF-03 | E2E y API |
| CP-03 | Correo inválido | `laura@` | «Escribe un correo válido» | RF-04 | E2E y API |
| CP-04 | Semestre fuera de rango | 0, 13 y «abc» | 400 con error en `semester` | RF-04, RF-12 | API |
| CP-05 | Archivo no PDF | `hoja.docx` | «Solo se permiten archivos PDF» | RF-02, RF-04 | E2E y API |
| CP-06 | PDF muy pesado | PDF de 8 MB | 413 / «La hoja de vida no puede pesar más de 5 MB» | RF-02, RF-04 | E2E y API |
| CP-07 | Correo duplicado | Correo ya registrado, con otras mayúsculas | 409 y «Ya existe un registro con este correo» | RF-12 | API |
| CP-08 | API sin nombre | POST directo sin `fullName` | 400; no se guarda nada ni queda archivo | RF-12 | API |
| CP-09 | Lista con datos | 3 registros | 3 filas, la más reciente primero | RF-06, RF-10 | API |
| CP-10 | Lista vacía | Base sin registros | «No hay practicantes registrados» | RF-06 | E2E |
| CP-11 | Ver detalle | Clic en un practicante | Todos los datos de RF-07 visibles | RF-07 | API y E2E |
| CP-12 | Marcar Viable | `PENDING` → «Viable» en la fila de la lista y recargar | `VIABLE` se conserva; `reviewedAt` lleno | RF-08, RF-11 | API y E2E |
| CP-13 | Estado inválido | PATCH con `"MAYBE"` | 400; estado sin cambios | RF-11 | API |
| CP-14 | Panel sin sesión | Abrir `/panel.html` y `GET /interns` sin token | Redirige al login; la API responde 401 | RF-13 | API y E2E |
| CP-15 | Login incorrecto | Contraseña errónea | 401 y «Usuario o contraseña incorrectos» | RF-13 | API |
| CP-16 | Descargar hoja de vida | Clic en «Descargar» | Se descarga el mismo PDF, con el nombre de RF-14 | RF-14 | API y E2E |
| CP-17 | Sin tratamiento de datos | Casilla sin marcar | 400 y el mensaje de RF-15 | RF-15 | E2E y API |
| CP-18 | Celular inválido | `2001234567` y `30012345` | «Escribe un celular colombiano…» | RF-01, RF-04 | E2E y API |
| CP-19 | Universidad «Otra» | «Otra» + «Universidad de Cundinamarca» | Se guarda «Universidad de Cundinamarca» | RF-01 | API |
| CP-20 | «Otra» sin texto | Carrera «Otra» y texto vacío | «Escribe el nombre de tu carrera» | RF-01, RF-03 | E2E y API |
| CP-21 | PDF falso | Archivo de texto renombrado a `.pdf` | «Solo se permiten archivos PDF» | RF-02 | API |
| CP-22 | Filtrar por estado | 2 pendientes y 1 viable; pestaña «Pendientes» | 2 filas; conteos 3 / 2 / 1 / 0 | RF-16 | API y E2E |
| CP-23 | Cambiar decisión con observación | `VIABLE` → `NOT_VIABLE` con nota | Estado y nota nuevos; `reviewedAt` actualizado | RF-17, RF-18 | API |
| CP-24 | Volver a Pendiente | PATCH con `"PENDING"` | 400; estado sin cambios | RF-18 | API |
| CP-25 | Token vencido o alterado | Token con firma cambiada | 401 | RF-13 | API |

**Matriz de trazabilidad**

| Requerimiento | Casos |
|---|---|
| RF-01 | CP-01, CP-18, CP-19, CP-20 |
| RF-02 | CP-01, CP-05, CP-06, CP-21 |
| RF-03 | CP-02, CP-20 |
| RF-04 | CP-03, CP-04, CP-05, CP-06, CP-18 |
| RF-05 | CP-01 (E2E: mensajes de envío) |
| RF-06 | CP-09, CP-10 |
| RF-07 | CP-11 |
| RF-08 | CP-12 |
| RF-09 | CP-01 |
| RF-10 | CP-09 |
| RF-11 | CP-12, CP-13 |
| RF-12 | CP-04, CP-07, CP-08 |
| RF-13 | CP-14, CP-15, CP-25 |
| RF-14 | CP-16 |
| RF-15 | CP-17 |
| RF-16 | CP-22 |
| RF-17 | CP-23 |
| RF-18 | CP-23, CP-24 |

## 11. Datos de demostración

- **RF-19.** Con `DEMO_DATA=true`, el backend carga al arrancar **4 practicantes de ejemplo** con datos ficticios y un PDF de muestra: 2 pendientes, 1 viable con observación y 1 no viable.
  - Solo los carga si la tabla está vacía, así que reiniciar no los duplica.
  - Con `DEMO_DATA=false`, la base arranca vacía.
  - Los datos de ejemplo son inventados: ningún dato real entra al repositorio.

## 12. Fuera de alcance

Se puede mencionar como mejora futura en la sustentación:

- Despliegue en la nube y base de datos de servidor.
- Varios analistas, roles o registro de analistas.
- Historial de decisiones por practicante (hoy solo se guarda la última).
- Búsqueda por nombre o correo, y paginación.
- Bloqueo de la cuenta tras varios intentos fallidos de inicio de sesión.
- Notificaciones por correo al practicante.
- Que el practicante consulte o edite su registro.
- Pruebas de extremo a extremo con Playwright.

## 13. Decisiones

**10 de noviembre de 2026:**
- ~~Stack igual a Kronos (Spring Boot 4.1 + Angular 22)~~: reemplazado el 11 de noviembre (ver abajo).
- Se implementan los dos opcionales del reto: login (RF-13) y descarga (RF-14).

**11 de noviembre de 2026:**
- **Carrera y universidad:** lista + «Otra» con texto libre (sección 3.2).
- **Campos adicionales al reto:** universidad, celular y casilla de tratamiento de datos (RF-15).
- **Decisión del analista:** se puede cambiar entre Viable y No viable, pero no volver a Pendiente (RF-18).
- **Observación:** siempre opcional (RF-17).
- **Login:** JWT, como Kronos (sección 5).
- **Panel:** filtro por estado con conteos (RF-16); sin búsqueda.
- **Diseño:** paleta inspirada en el Banco de Bogotá, sin su logo ni su nombre (RNF-10).
- **Pruebas:** reemplazado el 11 de noviembre (ver abajo).
- **Propuestas sin consultar, que se pueden cambiar:** semestre de 1 a 12; celular solo colombiano; sesión de 8 horas en `sessionStorage`; listas en el código; datos de demostración (RF-19).

**11 de noviembre de 2026, cambio de stack** (antes de escribir código):
- **Backend: Python 3.12 + Flask 3.1** en vez de Spring Boot. Es una de las tres opciones que nombra el reto y se puede probar de punta a punta antes de la entrega.
- **Frontend: HTML, CSS y JavaScript puro**, como sugieren los pasos del reto, en vez de Angular. Flask sirve las páginas y la API en el mismo origen.
- **Datos:** `sqlite3` de Python con SQL directo y migraciones numeradas propias (RNF-02). Login con **JWT** (sección 5), sin cambios.
- **Pruebas:** pytest para la API y Playwright para el navegador (RNF-13).
- **Botones en la lista:** «Viable» y «No viable» también en cada fila, como pide el documento del reto (RF-08).
- **Alcance:** el correo no especifica otro reto; la base es el documento del reto (desarrollo).
- **Entrega:** hoy a las 11:00 a. m., con el repositorio público.
