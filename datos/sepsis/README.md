# Datos: Sepsis Cases - Event Log

Log de eventos de pacientes con sospecha de sepsis de un hospital de Países Bajos (sistema ERP hospitalario, datos desidentificados por la fuente).

**Fuente:** Mannhardt, F. (2016). *Sepsis Cases - Event Log*. 4TU.ResearchData. https://doi.org/10.4121/uuid:915d2bfb-7e84-49ad-a286-dc35f063a460
**Licencia:** *4TU General Terms of Use* (https://doi.org/10.4121/resource:terms_of_use), según los metadatos del DOI. Prohibido cualquier intento de reidentificación.

## `original/` — log oficial completo (usar en la Fase 4)

| Archivo | Descripción |
|---|---|
| `Sepsis Cases - Event Log.xes.gz` | Archivo oficial descargado de 4TU (202,508 bytes; MD5 `b5671166ac71eb20680d3c74616c43d2`). |
| `Sepsis Cases - Event Log.xes` | El mismo log descomprimido. |
| `sepsis_full_events.csv` | CSV plano generado con [`scripts/convertir_xes_a_csv.py`](../../scripts/convertir_xes_a_csv.py): una fila por evento, 32 columnas (id del caso + 31 atributos de evento). |

Contenido: 1,050 casos, 15,214 eventos y 16 actividades. 27 atributos propios: `Age`, `Diagnose`, `Leucocytes`, `CRP`, `LacticAcid` y 22 indicadores booleanos (criterios SIRS y estudios diagnósticos), más 4 atributos estándar de XES (`concept:name`, `time:timestamp`, `lifecycle:transition`, `org:group`). 110 casos tienen `Admission IC`; las altas van de `Release A` a `Release E` (782 casos).

Notas para la matriz de características:
- `Age`, `Diagnose` y los 22 indicadores aparecen en un evento temprano de cada caso (casi siempre `ER Registration`); deben tomarse por caso del evento que los tenga.
- Algunos eventos de laboratorio no tienen valor: `Leucocytes` 3,361 de 3,383, `CRP` 3,123 de 3,262 y `LacticAcid` 1,454 de 1,466.
- 268 casos no tienen ninguna actividad de alta.

## `benchmark_simplificado/` — versión sin atributos clínicos

| Archivo | Descripción |
|---|---|
| `Sepsis_Cases.csv` | Columnas `case_id`, `Activity`, `end_time`. |
| `Sepsis_Cases.xes` | El mismo log en XES (solo `concept:name` y `time:timestamp`). |

1,050 casos y 15,214 eventos, sin edad, diagnóstico ni laboratorios. Sirve solo como referencia para minería de procesos; **no es apta para la Fase 4**.

## Pendiente

El script de auditoría de la Fase 4 (leucocitos, PCR, lactato, edad y altas) y la matriz de características todavía no están en el repositorio.
