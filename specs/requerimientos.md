# Requerimientos – Plataforma Básica de Selección de Practicantes

## 1. Contexto y alcance

La plataforma permite que los practicantes registren sus datos y su hoja de vida en PDF, y que un analista de selección los revise y los marque como **Viable** o **No viable**. Corre en local, sin despliegue en la nube. Corresponde al reto *Kata Practicing – Challenge 1* de la Vicepresidencia de Tecnología, con sustentación de 5 a 7 minutos el 12 de noviembre de 2026 a las 10:00 a. m.

**Actores**

| Actor | Qué hace | Acceso |
|---|---|---|
| Practicante | Llena el formulario y sube su hoja de vida | Público, sin login |
| Analista de selección | Consulta la lista, ve el detalle, descarga el PDF y marca Viable / No viable | Protegido con usuario y contraseña (opcional) |

**Supuestos**

- Un único rol de analista con credenciales fijas, configuradas en el servidor.
- Todo practicante nuevo queda en estado **Pendiente** hasta que el analista decida.
- El analista puede cambiar su decisión en cualquier momento.
- Un correo electrónico solo puede registrarse una vez.

⚠️ **Por confirmar:** si el reto que corresponde es el de desarrollo (este PDF) o una kata de tester, como dice el mensaje de WhatsApp.

## 2. Requerimientos funcionales

Son 14: los RF-01 a RF-12 son obligatorios y los RF-13 y RF-14 son los desafíos opcionales.

| ID | Módulo | Requerimiento | Prioridad |
|---|---|---|---|
| RF-01 | Formulario | Capturar nombre completo, correo electrónico, carrera universitaria y semestre actual | Obligatorio |
| RF-02 | Formulario | Permitir adjuntar la hoja de vida en formato PDF | Obligatorio |
| RF-03 | Formulario | Validar que todos los campos sean obligatorios antes de enviar | Obligatorio |
| RF-04 | Formulario | Validar formato de correo, semestre numérico entre 1 y 12, archivo .pdf de máximo 5 MB | Obligatorio |
| RF-05 | Formulario | Mostrar mensaje de éxito al registrar y mensaje de error claro por campo | Obligatorio |
| RF-06 | Panel | Listar los practicantes registrados con nombre, carrera, semestre y estado | Obligatorio |
| RF-07 | Panel | Ver el detalle completo de un practicante | Obligatorio |
| RF-08 | Panel | Botones «Viable» y «No viable» que cambian el estado y se reflejan de inmediato | Obligatorio |
| RF-09 | API | Guardar un practicante con su archivo | Obligatorio |
| RF-10 | API | Consultar la lista de practicantes | Obligatorio |
| RF-11 | API | Actualizar el estado de un practicante (Viable / No viable) | Obligatorio |
| RF-12 | API | Repetir en el servidor las validaciones de RF-03 y RF-04 y rechazar correos duplicados | Obligatorio |
| RF-13 | Seguridad | Login de analista: sin sesión válida no se puede ver el panel ni llamar la API de consulta y estado | Opcional |
| RF-14 | Panel | Descargar la hoja de vida PDF desde el panel | Opcional |

## 3. Requerimientos no funcionales

| ID | Categoría | Requerimiento |
|---|---|---|
| RNF-01 | Ejecución | Funciona en local; no requiere nube ni Docker |
| RNF-02 | Persistencia | Base de datos local SQLite en un único archivo; se crea sola al iniciar |
| RNF-03 | Archivos | Los PDF se guardan en una carpeta del servidor con nombre único; la BD guarda solo el nombre |
| RNF-04 | Tecnología | Front-end en Angular (HTML, CSS y TypeScript); back-end en Java 21 con Spring Boot; solo herramientas gratuitas |
| RNF-05 | Usabilidad | Formulario y panel claros, con estados visibles por color (Pendiente, Viable, No viable) |
| RNF-06 | Seguridad | Solo se aceptan PDF; nombres de archivo saneados; credenciales del analista fuera del código y del cliente |
| RNF-07 | Mantenibilidad | Código organizado por capas y versionado en Git con GitHub Flow |
| RNF-08 | Documentación | README con requisitos, instalación, ejecución, credenciales de prueba y capturas de pantalla |
| RNF-09 | Rendimiento | Las respuestas de la API tardan menos de 1 segundo con 100 registros en local |

## 4. Modelo de datos y contrato de la API

Una sola tabla y seis endpoints REST que intercambian JSON, salvo el registro, que usa `multipart/form-data` por el archivo. Los nombres en el código van en inglés.

**Tabla `interns`**

| Campo | Tipo | Reglas |
|---|---|---|
| `id` | INTEGER | Llave primaria, autoincremental |
| `full_name` | TEXT | Obligatorio, 3 a 100 caracteres |
| `email` | TEXT | Obligatorio, formato válido, único |
| `career` | TEXT | Obligatorio |
| `semester` | INTEGER | Obligatorio, 1 a 12 |
| `cv_file_name` | TEXT | Nombre del PDF guardado en la carpeta de archivos |
| `status` | TEXT | `PENDING`, `VIABLE` o `NOT_VIABLE`; por defecto `PENDING` |
| `created_at` | TEXT | Fecha y hora de creación |

**Endpoints** (prefijo `/api/v1`)

| Método | Ruta | Uso | Respuestas | RF |
|---|---|---|---|---|
| POST | `/interns` | Registrar practicante (campos + `cv` PDF) | 201 creado; 400 validación; 409 correo duplicado | RF-09, RF-12 |
| GET | `/interns` | Listar practicantes | 200 lista; 401 sin sesión | RF-10 |
| GET | `/interns/{id}` | Ver detalle | 200; 404 no existe | RF-07 |
| PATCH | `/interns/{id}/status` | Cambiar estado, cuerpo `{"status":"VIABLE"}` | 200; 400 estado inválido; 404 | RF-11 |
| GET | `/interns/{id}/cv` | Descargar el PDF | 200 archivo; 404 | RF-14 |
| POST | `/auth/login` | Iniciar sesión del analista | 200; 401 credenciales inválidas | RF-13 |

## 5. Historias de usuario y criterios de aceptación

**HU-01 – Registro del practicante** (RF-01 a RF-05, RF-09, RF-12)
Como practicante, quiero registrar mis datos y mi hoja de vida para postularme a la práctica.

```gherkin
Escenario: Registro exitoso
  Dado que estoy en el formulario de registro
  Cuando diligencio todos los campos con datos válidos y adjunto un PDF
  Y presiono "Enviar"
  Entonces veo el mensaje "Registro exitoso"
  Y mi registro queda guardado con estado "Pendiente"

Escenario: Campo obligatorio vacío
  Dado que estoy en el formulario de registro
  Cuando dejo el nombre vacío y presiono "Enviar"
  Entonces veo el mensaje "El nombre es obligatorio"
  Y el formulario no se envía

Escenario: Archivo que no es PDF
  Cuando adjunto un archivo .docx
  Entonces veo el mensaje "Solo se permiten archivos PDF"
```

**HU-02 – Lista de practicantes** (RF-06, RF-10)
Como analista, quiero ver la lista de practicantes registrados para saber a quién revisar.

```gherkin
Escenario: Ver lista
  Dado que existen practicantes registrados
  Cuando ingreso al panel
  Entonces veo una fila por practicante con nombre, carrera, semestre y estado

Escenario: Lista vacía
  Dado que no hay registros
  Cuando ingreso al panel
  Entonces veo el mensaje "No hay practicantes registrados"
```

**HU-03 – Detalle y decisión** (RF-07, RF-08, RF-11)
Como analista, quiero ver la información de un practicante y marcarlo como Viable o No viable.

```gherkin
Escenario: Marcar como viable
  Dado que veo el detalle de un practicante en estado "Pendiente"
  Cuando presiono "Viable"
  Entonces su estado cambia a "Viable" en el panel
  Y el cambio se conserva al recargar la página
```

**HU-04 – Acceso restringido** (RF-13, opcional)
Como analista, quiero iniciar sesión para que solo yo vea el panel.

```gherkin
Escenario: Acceso sin sesión
  Dado que no he iniciado sesión
  Cuando intento abrir el panel
  Entonces soy redirigido al login

Escenario: Credenciales inválidas
  Cuando ingreso una contraseña incorrecta
  Entonces veo "Usuario o contraseña incorrectos"
```

**HU-05 – Descarga de hoja de vida** (RF-14, opcional)
Como analista, quiero descargar la hoja de vida para revisarla en detalle.

```gherkin
Escenario: Descargar PDF
  Dado que veo el detalle de un practicante
  Cuando presiono "Descargar hoja de vida"
  Entonces se descarga el PDF que subió el practicante
```

## 6. Casos de prueba y trazabilidad

Los casos marcados como API se ejecutan con Postman o curl, sin pasar por el formulario, para comprobar que el servidor valida por su cuenta.

| ID | Caso | Datos de entrada | Resultado esperado | RF |
|---|---|---|---|---|
| CP-01 | Registro exitoso | Datos válidos + PDF de 200 KB | «Registro exitoso»; queda en Pendiente | RF-01, RF-02, RF-05, RF-09 |
| CP-02 | Nombre vacío | Nombre en blanco | «El nombre es obligatorio»; no se envía | RF-03 |
| CP-03 | Correo inválido | `laura@` | Error de formato de correo | RF-04 |
| CP-04 | Semestre fuera de rango | 0, 13 y «abc» | Error de semestre | RF-04 |
| CP-05 | Archivo no PDF | `hoja.docx` | «Solo se permiten archivos PDF» | RF-02, RF-04 |
| CP-06 | PDF muy pesado | PDF de 8 MB | Error de tamaño máximo | RF-04 |
| CP-07 | Correo duplicado | Correo ya registrado | 409 y mensaje de correo existente | RF-12 |
| CP-08 | API sin nombre | POST directo sin `fullName` | 400; no se guarda nada | RF-12 |
| CP-09 | Lista con datos | 3 registros | 3 filas con nombre, carrera, semestre y estado | RF-06, RF-10 |
| CP-10 | Lista vacía | BD sin registros | «No hay practicantes registrados» | RF-06 |
| CP-11 | Ver detalle | Clic en un practicante | Todos sus datos visibles | RF-07 |
| CP-12 | Marcar Viable | Clic en «Viable» y recargar | Estado Viable se conserva | RF-08, RF-11 |
| CP-13 | Estado inválido | PATCH con `"MAYBE"` | 400; estado sin cambios | RF-11 |
| CP-14 | Panel sin sesión | Abrir `/panel` sin login | Redirige al login | RF-13 |
| CP-15 | Login incorrecto | Contraseña errónea | «Usuario o contraseña incorrectos» | RF-13 |
| CP-16 | Descargar hoja de vida | Clic en «Descargar» | Se descarga el mismo PDF subido | RF-14 |

**Matriz de trazabilidad**

| Requerimiento | Casos que lo prueban |
|---|---|
| RF-01 | CP-01 |
| RF-02 | CP-01, CP-05 |
| RF-03 | CP-02 |
| RF-04 | CP-03, CP-04, CP-05, CP-06 |
| RF-05 | CP-01 |
| RF-06 | CP-09, CP-10 |
| RF-07 | CP-11 |
| RF-08 | CP-12 |
| RF-09 | CP-01 |
| RF-10 | CP-09 |
| RF-11 | CP-12, CP-13 |
| RF-12 | CP-07, CP-08 |
| RF-13 | CP-14, CP-15 |
| RF-14 | CP-16 |

## 7. Fuera de alcance

Se puede mencionar como mejora futura en la sustentación:

- Despliegue en la nube.
- Varios analistas, roles o registro de usuarios analistas.
- Notificaciones por correo al practicante.
- Filtros, búsqueda y paginación en el panel.
- Edición o eliminación de registros.
