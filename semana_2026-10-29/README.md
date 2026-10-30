# Semana del 29 de octubre de 2026: exploración, limpieza y verificación del log Sepsis Cases

**Autora:** Jessica Melani Romero Lora
**Proyecto:** Detección y exclusión de variables circulares en modelos de ingreso a UCI
**Fase:** 1 de 4 (exploración, carga y verificación del dataset)

## 1. Propósito

Verificar que el log de eventos *Sepsis Cases* (Mannhardt, 2016) cumple la documentación del repositorio (1,050 casos, 15,214 eventos, 16 actividades y 27 atributos propios) antes de realizar la auditoría temporal de la Fase 2. En esta etapa no se entrena ningún modelo ni se interpreta el desempeño predictivo.

## 2. Fuente y entorno

- **Fuente primaria:** `Sepsis Cases - Event Log.xes`, copia del archivo oficial de 4TU.ResearchData (https://doi.org/10.4121/uuid:915d2bfb-7e84-49ad-a286-dc35f063a460).
- **Fuente derivada:** `sepsis_full_events.csv`, generado a partir del XES con `scripts/convertir_xes_a_csv.py`.
- **Entorno:** macOS, Python 3 (distribución Miniconda), pandas, git 2.39.5.

## 2.1 Glosario

| Término | Definición |
|---|---|
| **Log de eventos** | Registro en el que cada fila es una actividad ejecutada sobre un caso, con su marca de tiempo y atributos. Es el formato base de la minería de procesos. |
| **Caso (*case*)** | Unidad de análisis. En este log, un caso es la trayectoria de un paciente desde su registro en urgencias hasta su alta. |
| **Traza** | Secuencia ordenada de eventos de un mismo caso. En el archivo XES, cada traza está delimitada por la etiqueta `<trace>`. |
| **Evento** | Una actividad registrada en un momento dado (por ejemplo, `Leucocytes` o `Admission IC`). |
| **XES** | *eXtensible Event Stream*. Formato estándar en XML para logs de eventos, definido por la IEEE. |
| **CSV** | *Comma-Separated Values*. Tabla de texto en la que cada fila es un registro y cada columna un atributo. Aquí es la versión aplanada del XES. |
| **ER (*Emergency Room*)** | Servicio de urgencias del hospital. Es el punto de entrada del paciente al sistema. |
| **Triage** | Clasificación rápida de la gravedad de un paciente al llegar a urgencias, para decidir la prioridad de atención. `ER Triage` y `ER Sepsis Triage` son dos evaluaciones de este tipo. |
| **Sepsis** | Respuesta sistémica y desregulada del organismo a una infección, que puede causar disfunción de órganos y, si no se trata, la muerte. |
| **SIRS** | *Systemic Inflammatory Response Syndrome*. Conjunto de criterios clínicos de respuesta inflamatoria (temperatura, frecuencia cardiaca, frecuencia respiratoria y leucocitos). Sirve para identificar sepsis en urgencias. |
| **UCI (IC, *Intensive Care*)** | Unidad de cuidados intensivos. El evento `Admission IC` registra el ingreso del paciente a esta unidad. Es el desenlace que predice la tesis. |
| **NC (*Normal Care*)** | Unidad de cuidado normal (sala general). El evento `Admission NC` registra el ingreso a esta unidad. Un caso con `Admission NC` y sin `Admission IC` es un negativo. |
| **IV (*Intravenous*)** | Administración por vía intravenosa, como `IV Antibiotics` (antibióticos) o `IV Liquid` (líquidos). |
| **Leucocitos** | Glóbulos blancos en sangre. Un valor alterado forma parte de los criterios SIRS. |
| **CRP** | Proteína C reactiva. Marcador de inflamación medido en sangre. |
| **Lactato (*LacticAcid*)** | Metabolito en sangre. Valores elevados indican hipoperfusión tisular, asociada a gravedad en sepsis. |
| **Atributo** | Columna del dataset que describe un evento o un caso (por ejemplo, `Age` o `CRP`). |
| **Variable circular** | Atributo que contiene información del propio desenlace y, por eso, no está disponible en el momento de predecirlo. Puede ser *definicional* (define el desenlace), *temporal* (se registra después del desenlace) o *proxy* (sustituye al desenlace). Es el objeto de estudio de la tesis. |
| **Fuga de información (*leakage*)** | Uso, durante el entrenamiento o la evaluación de un modelo, de información que no existiría al momento de la predicción. Produce métricas infladas. |
| **Primer evento** | Primera fila de cada traza en orden de tiempo. Representa el momento de la predicción: el registro en urgencias. |
| **Valor faltante** | Celda sin dato. Aquí, un atributo que no se registró en el evento considerado. |
| **Clase positiva / negativa** | Clase positiva: el caso tiene `Admission IC`. Clase negativa: no lo tiene. |

## 3. Decisiones y razones

| # | Decisión | Razón |
|---|---|---|
| D1 | Usar el XES oficial como fuente de verdad. | Es el archivo que documenta el README y contiene los atributos clínicos completos. El benchmark simplificado no es apto para la Fase 4. |
| D2 | Verificar la copia con `cmp` y eliminar el duplicado `Sepsis_Cases.xes.gz`. | Dos copias idénticas del mismo dato generan riesgo de usar la equivocada. |
| D3 | No modificar `datos/sepsis/original/`. Las correcciones se escriben en `datos/sepsis/procesado/`. | Preserva el dato original para trazabilidad y reproducción. |
| D4 | Conservar la traza sin identificador y asignarle `caso_sin_identificador`, en lugar de descartarla. | Su secuencia clínica es completa (registro en urgencias a alta), no contiene `Admission IC` y el README reporta 1,050 casos. |
| D5 | Verificar con `assert` que la traza sin identificador no contenga `Admission IC` antes de asignarle un nombre. | Si la traza fuera positiva, la asignación cambiaría el número de positivos. El script se detiene en ese caso. |
| D6 | Definir el primer evento como la fila completa con menor marca de tiempo por caso (`sort_values` estable seguido de `drop_duplicates`). | El método anterior, `groupby().first()`, toma el primer valor no nulo de cada columna por separado. Eso asigna a un atributo un valor registrado en otro evento y produce una disponibilidad ficticia en el momento de la predicción. |
| D7 | Excluir `lifecycle:transition` y `org:group` del análisis de atributos. | Son metadatos del estándar XES, no variables clínicas. |
| D8 | Comparar el XES y el CSV traza por traza. | Descarta pérdida o alteración de eventos durante la conversión. |

## 4. Resultados

| Verificación | Resultado | Fuente |
|---|---|---|
| Trazas en el XES | 1,050 | `fase1_diagnostico_casos.txt` |
| Eventos en el XES (conteo con `grep`) | 15,214 | Terminal, comando `grep -o "<event>"` |
| Eventos en el CSV | 15,214 | `fase1_verificacion.txt` |
| Actividades distintas | 16 | `fase1_verificacion.txt` |
| Filas sin identificador en el CSV | 24 (una traza) | `fase1_diagnostico_casos.txt` |
| Trazas del XES sin eventos | 0 | `fase1_diagnostico_casos.txt` |
| Diferencias de eventos XES vs. CSV | 0 | `fase1_diagnostico_casos.txt` |
| Casos tras la corrección | 1,050 | `fase1_corregir_identificador.txt` |
| Filas en el primer evento | 1,050 (una por caso) | `fase1_verificacion.txt` |
| Casos con `Admission IC` | 110 (10.5 %) | `fase1_verificacion.txt` |
| Casos sin `Admission IC` | 940 | Cálculo: 1,050 − 110 |

**Traza sin identificador.** Contiene 24 eventos consecutivos, desde `ER Registration` hasta `Release C`. Incluye dos eventos `Admission NC` y ningún `Admission IC`. Su primer evento es `ER Registration` (2014-11-10T01:45:19+01:00). Es un caso negativo válido.

## 5. Limitaciones

- El README documenta 27 atributos propios. Este número debe confirmarse en `fase1_verificacion.txt`.
- La tabla de faltantes en el primer evento describe disponibilidad en el registro, no su valor clínico. Su interpretación se realiza en la Fase 2.
- El log proviene de un único hospital de Países Bajos. Los resultados no son generalizables sin validación externa.

## 6. Pendientes

- Clasificar cada atributo como válido o circular (definicional, temporal o *proxy*), Fase 2.
- Documentar en la tesis la decisión D4 y su justificación.
- Confirmar el número de atributos propios frente a la documentación oficial.

## 7. Reproducibilidad

Desde la raíz del repositorio:

```bash
./scripts/publicar_semana.sh semana_2026-10-29 "mensaje del commit"
```

El script ejecuta los scripts de la Fase 1 en orden, guarda sus salidas en `resultados/` y publica los cambios en GitHub.
