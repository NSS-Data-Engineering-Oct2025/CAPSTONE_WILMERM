# Resumen de la Conversacion con el Instructor — Capstone DE

**Fecha de creacion:** 29 de abril de 2026
**Contexto:** Reunion entre Wilmer y el instructor del bootcamp de Data Engineering para aclarar expectativas del proyecto capstone y la presentacion final (Demo Day).

---

## 1. Que se espera de la presentacion (Demo Day)

- **No mostrar codigo en vivo.** La presentacion es de alto nivel, tipo reporte visual, no una demo tecnica profunda.
- **Duracion estricta: 10 minutos.** El instructor usa un cronometro y ha cortado presentaciones a la mitad del tiempo. Es un formato muy apretado.
- **Formato:** Slide deck (PowerPoint), dashboard interactivo embebido, o similar. No es una sesion de live coding.
- **Tener recursos disponibles por si alguien quiere profundizar** — por ejemplo, el repositorio abierto, un diagrama de Airflow/Prefect, modelos de dbt — pero esto es solo si un asistente tecnico lo pide, no como parte de la presentacion.

---

## 2. Contenido del slide deck — Enfoque de Data Engineer

El instructor fue muy claro: **el slide deck NO es una presentacion de preguntas de negocio y respuestas.** Eso es para analistas de datos.

Como Data Engineer, la presentacion debe hablar sobre:

| Tema | Detalle |
|------|---------|
| **El pipeline** | Como se construyo, como se ejecuta, como fluye la data |
| **Tecnologias elegidas** | Cuales se usaron y **por que** se eligieron |
| **Arquitectura** | Diagrama de alto nivel del flujo de datos |
| **Dificultades / Struggles** | Que problemas se encontraron y como se resolvieron |
| **Screenshots** | Capturas que demuestren que todo funciono en algun momento |
| **Dashboard (opcional)** | Se puede embeber o mostrar un dashboard, pero no es el foco principal |

---

## 3. Rol del Data Engineer vs. Data Analyst

El instructor enfatizo la diferencia clave:

- **Data Engineer:** Toma datos desordenados de multiples fuentes, los combina, limpia y procesa a traves de pipelines (Python, SQL, Snowflake, etc.), y los deja disponibles para que alguien mas los use.
- **Data Analyst:** Hace preguntas de negocio y las responde con los datos.

> *"Nuestro trabajo es tomar toda esta data desordenada, pasarla por pipelines, y tenerla disponible para que alguien venga y la use. No estamos respondiendo preguntas sobre la data — eso es el rol de otra persona."*

**Ejemplo dado por el instructor:** "Encontre 12 fuentes distintas de datos de accidentes de motocicleta. Las combine, las procese, las limpie. Aqui esta la data disponible para que alguien haga un analisis. Aqui esta mi dashboard donde puedes ver de alto nivel que datos tengo. Pero yo no estoy haciendo ni respondiendo preguntas sobre los datos."

---

## 4. Tipos de audiencia en la presentacion

| Audiencia | Que pueden preguntar |
|-----------|---------------------|
| **Stakeholders / No-tecnicos** | Sobre la data en si, como se podria usar, cuales fueron las dificultades |
| **Personas tecnicas** | Como se construyo el Airflow/Prefect, como se conecto dbt, como se resolvieron problemas tecnicos especificos |

La clave es tener material disponible para ambos tipos, pero la presentacion en si es de alto nivel.

---

## 5. Ensayos / Rehearsals y Fechas Clave

- Habra **una presentacion de ensayo** ante el instructor y un invitado.
- Sera aproximadamente **una semana antes del Demo Day.**
- El instructor ayudara a ajustar: si hay demasiado contenido, si falta algo, si el ritmo es correcto.
- Wilmer puede acercarse al instructor en cualquier momento cuando empiece a dar forma a la presentacion.

### Calendario del Capstone

| Fecha | Evento | Detalle |
|-------|--------|---------|
| **5/9/2026** | Primer walkthrough con el instructor | Sentarse con el instructor y caminar por toda la arquitectura. **No necesita estar terminado.** El instructor identifica gotchas y problemas |
| **5/16/2026** | Practica de presentacion del capstone | El instructor invita personas externas. 10 minutos por estudiante. Se espera estar al **85-87% de avance.** Tener slide deck listo para hablar. Instructores y externos dan un primer vistazo |
| **5/27/2026** | Dia de graduacion | - |
| **5/29/2026** | **Demo Day** | Presentacion final |

Los recursos y horarios estan disponibles en el documento "DE October 2025 scheduled doc" (online).

---

## 6. Arquitectura del proyecto de Wilmer

Segun lo discutido, el flujo de datos del capstone es:

1. **Ingestion** — Scripts de Python traen data de multiples fuentes
2. **PostgreSQL** — La data cruda se carga primero en Postgres
3. **dbt** — Limpieza y transformaciones (staging, intermediate, marts)
4. **Duck Lake** — La data transformada se mueve a Duck Lake (no solo DuckDB simple)

---

## 7. Conceptos de DuckDB discutidos

| Concepto | Descripcion |
|----------|-------------|
| **DuckDB local** | Se levanta localmente, se llena con data (scaffold). Cada persona tiene su propia instancia |
| **MotherDuck** | Version cloud de Duck Lake y DuckDB. Solo se cambian connection strings para apuntar a la nube |
| **WASM (WebAssembly)** | DuckDB corriendo en el navegador. Util para herramientas de aprendizaje donde cada usuario tiene su propio DuckDB en el browser |
| **Embedded Analytics** | DuckDB embebido dentro de una aplicacion, similar a SQLite. Se envia con la app y los datos se inicializan automaticamente |
| **Duck Lake** | Concepto de DuckDB + lakehouse architecture. No es una base de datos compartida tradicional — cada quien obtiene su propio "slice" de datos |
| **DuckDB `:memory:`** | Cuando te conectas a `DuckDB:memory:`, lo estas usando como **SQL query engine**, no como una base de datos DuckDB persistente |

### Duck Lake en la nube — Ejemplo del instructor

El instructor mostro su propia arquitectura en produccion:

- **Catalogo de Duck Lake** almacenado en **Aurora RDS Postgres en AWS**
- **Datos** almacenados en **S3 buckets en formato Parquet**
- Cualquier persona con una conexion DuckDB **in-memory** puede conectarse a ese catalogo de Postgres instantaneamente
- Multiples personas pueden hacer queries al mismo catalogo sin conflictos

### Problema: Metabase + DuckDB compartiendo archivo

Wilmer reporto un problema que tuvo:
- Metabase estaba corriendo en localhost y funcionaba bien
- Despues de hacer la visualizacion, al regresar a verificar el SQL init query, empezaba a dar errores
- **Causa raiz:** Metabase y otro proceso estaban compartiendo la misma instancia de archivo DuckDB con el catalogo. Esto causa crashes porque DuckDB file no soporta acceso concurrente de multiples procesos.
- **Solucion del instructor:** El catalogo (archivo DuckDB) deberia convertirse en una **instancia de catalogo en Postgres**. Se conecta a Postgres en lugar del archivo DuckDB, y se eliminan los problemas de concurrencia.

---

## 8. Fuentes de datos — CSVs vs APIs en vivo

Wilmer pregunto: que pasa si las fuentes de datos resultan ser CSVs estaticos en vez de APIs en vivo?

- **Respuesta del instructor:** Esta bien. La mayoria de las veces, si son CSVs, se descargan con un boton o un link.
- Se puede usar **HTTPX** para hacer GET al endpoint de descarga y bajar el CSV programaticamente. Es lo mismo que hace un browser al descargar.
- Esto es aceptable para **1-2 datasets**.
- Wilmer menciono que tiene un dataset adicional de ~**6 millones de filas** que necesita actualizacion semanal. El instructor confirmo que esta bien.
- Si hay dudas sobre un dataset especifico, mandar un **Slack** al instructor.

---

## 9. Idea alternativa de datos — Futbol / Soccer

El instructor sugirio una idea interesante para datos de futbol/soccer:

- Hay fuentes de datos disponibles para jugadores, equipos, etc.
- Un angulo interesante: **las relaciones y el reclutamiento** — como los jugadores se mueven entre equipos, quien conocio a quien.
- Mapear el **movimiento de jugadores** y las conexiones entre ellos seria un enfoque de data engineering valioso.

---

## 10. Puntos clave para recordar

- [ ] La presentacion habla del **pipeline**, no de preguntas de negocio
- [ ] Maximo **10 minutos** — ser conciso
- [ ] Tener el **repo y recursos tecnicos** disponibles por si alguien lo pide
- [ ] Incluir **screenshots** que demuestren que el pipeline funciono
- [ ] Explicar las **tecnologias elegidas y por que**
- [ ] Hablar de los **struggles** y como se resolvieron
- [ ] Investigar **MotherDuck** como opcion cloud para Duck Lake
- [ ] **5/9/2026** — Primer walkthrough con el instructor (no necesita estar terminado)
- [ ] **5/16/2026** — Practica de presentacion (tener slide deck, 85-87% listo)
- [ ] **5/29/2026** — Demo Day
- [ ] Mover el catalogo DuckDB file a **Postgres** para evitar crashes de concurrencia
- [ ] Datasets CSV se pueden descargar con **HTTPX** — es valido para el capstone
