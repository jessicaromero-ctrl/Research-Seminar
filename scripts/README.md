# Scripts del repositorio

Este directorio contiene los programas que generan los resultados de la investigación. Todos se ejecutan desde la **raíz del repositorio**, porque sus rutas son relativas a esa carpeta (por ejemplo, `datos/sepsis/original/`).

Ningún script modifica `datos/sepsis/original/`. Las correcciones se escriben en `datos/sepsis/procesado/` (decisión D3 de la bitácora de la semana).

## Orden de ejecución

El orden importa porque cada script puede depender de la salida de otro.

| Orden | Script | Depende de | Genera |
|---|---|---|---|
| 0 | `convertir_xes_a_csv.py` | XES oficial | CSV de eventos (en `datos/sepsis/original/`) |
| 1 | `fase1_diagnostico_casos.py` | XES oficial y CSV original | Reporte de trazas (solo lectura) |
| 2 | `fase1_traza_sin_identificador.py` | CSV original | Secuencia de la traza sin nombre (solo lectura) |
| 3 | `fase1_corregir_identificador.py` | CSV original | CSV procesado con identificador asignado |
| 4 | `fase1_verificacion.py` | CSV procesado | Resumen, balance de clase y faltantes por atributo |
| — | `publicar_semana.sh` | Todos los anteriores | Ejecuta los scripts de la semana, guarda sus salidas y publica en GitHub |

`publicar_semana.sh` no es un análisis: es el orquestador que reproduce la Fase 1 completa.

---

## 1. `convertir_xes_a_csv.py`

**Origen:** incluido en el repositorio original; no fue escrito durante la semana.

**Qué hace.** Lee el archivo XES oficial y lo convierte en una tabla CSV con una fila por evento. Imprime un resumen de casos, eventos, actividades, atributos e ingresos a UCI.

**Por qué existe.** El XES es un formato XML que no se analiza directamente con pandas. El CSV permite contar, filtrar y calcular faltantes con operaciones simples.

**Decisión asociada.** Se usa como puente entre la fuente oficial (XES) y el análisis (CSV). La verificación de su salida se hizo en la Fase 1 mediante el diagnóstico de trazas.

---

## 2. `fase1_diagnostico_casos.py`

**Qué hace.** Compara el XES oficial con el CSV traza por traza. Verifica tres cosas: trazas sin eventos, trazas presentes en el XES y ausentes en el CSV, y trazas con número distinto de eventos en ambos archivos.

**Por qué existe.** El log documenta 1,050 casos, pero el CSV contenía 1,049 identificadores distintos. Este script localiza la causa en lugar de asumirla.

**Resultado principal.** Una traza sin identificador de caso, con 24 eventos. Ninguna traza está vacía y la conversión no altera el número de eventos (ver `semana_2026-10-29/resultados/fase1_diagnostico_casos.txt`).

**Decisión asociada.** D8 (comparar XES y CSV traza por traza).

---

## 3. `fase1_traza_sin_identificador.py`

**Qué hace.** Extrae los eventos sin identificador de caso y muestra su secuencia de actividades y marcas de tiempo. Verifica si contienen `Admission IC`.

**Por qué existe.** Antes de decidir cómo tratar la traza sin nombre, había que saber qué contiene. Si fuera un caso positivo, la decisión cambiaría el número de positivos (decisión D5).

**Resultado principal.** La traza corresponde a un paciente completo, desde `ER Registration` hasta `Release C`, con dos `Admission NC` y ningún `Admission IC`. Es negativa.

**Decisión asociada.** D4 y D5.

---

## 4. `fase1_corregir_identificador.py`

**Qué hace.** Asigna el identificador `caso_sin_identificador` a los eventos sin nombre de caso. Antes de hacerlo, verifica con `assert` que esos eventos no contengan `Admission IC`. Guarda el resultado en `datos/sepsis/procesado/sepsis_events_corregido.csv`.

**Por qué existe.** Descartar la traza habría dejado 1,049 casos, en contradicción con la documentación del log. Asignarle un identificador conserva el caso sin modificar su contenido.

**Por qué el `assert`.** Es una comprobación automática de la decisión D5. Si el dato cambiara en el futuro, el script se detiene en lugar de producir un resultado incorrecto en silencio.

**Resultado principal.** 1,050 casos únicos tras la corrección.

**Decisiones asociadas.** D3, D4 y D5.

---

## 5. `fase1_verificacion.py`

**Qué hace.** Lee el CSV procesado y calcula tres cosas: conteo de casos, eventos y actividades; balance de clase para `Admission IC`; y porcentaje de faltantes por atributo, tanto en el conjunto completo de eventos como en el primer evento de cada caso.

**Por qué existe.** Es la verificación formal de que el dataset cumple lo que documenta el README antes de la auditoría temporal de la Fase 2.

**Método del primer evento.** La función `primer_evento` ordena por caso y tiempo, y conserva la fila completa del primer evento. No usa `groupby().first()`, porque ese método toma el primer valor no nulo de cada columna por separado, lo que mezcla valores de eventos distintos (decisión D6).

**Atributos excluidos.** `lifecycle:transition` y `org:group` son metadatos del estándar XES, no variables clínicas (decisión D7).

**Resultado principal.** 1,050 casos, 110 con `Admission IC`, 940 sin él, y 1,050 filas en el primer evento.

**Decisiones asociadas.** D6 y D7.

---

## 6. `publicar_semana.sh`

**Qué hace.** Ejecuta los scripts de una semana en orden, guarda cada salida en `<semana>/resultados/`, añade los cambios a Git, crea un commit y lo sube a GitHub.

**Uso.**

```bash
./scripts/publicar_semana.sh semana_2026-10-29 "mensaje del commit"
```

**Por qué existe.** Reproduce el análisis completo con un solo comando, y cada publicación queda ligada a las salidas que la respaldan.

**Protecciones.**

- `set -euo pipefail` detiene el script ante cualquier error. Así no se publican resultados parciales.
- `cd "$(dirname "$0")/.."` ubica la ejecución en la raíz del repositorio, sin importar desde dónde se llame.
- Si no hay cambios, no crea un commit vacío.
- Exige que exista el `README.md` de la semana antes de publicar.

**Limitación conocida.** El script ejecuta `git push` sin sincronizar antes. Si el remoto recibe cambios, el `push` falla (ocurrió en esta semana). La corrección recomendada es añadir `git pull --rebase origin main` antes del `push`.

**Decisiones asociadas.** D1 a D8, porque es el script que reproduce el flujo completo.

---

## Reglas de trabajo

- Cada script nuevo debe agregarse a esta tabla y a su sección, con su motivo.
- Cada decisión debe registrarse en la bitácora de la semana (`semana_2026-10-29/README.md`), con su número `D` correspondiente.
- Los scripts no deben editarse directamente en GitHub: los cambios se hacen en la computadora y se publican con `publicar_semana.sh`.

