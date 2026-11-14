# Semana del 2 al 13 de noviembre de 2026: Fase 2, clasificación de atributos

**Autora:** Jessica Melani Romero Lora
**Proyecto:** Detección y exclusión de variables circulares en modelos de ingreso a UCI
**Asesor:** Dr. Marcos Yamir Gómez
**Fase:** 2 de 4 (auditoría temporal, OE1)
**Última sesión registrada:** 13 de noviembre de 2026
**Estado:** en curso

## 1. Objetivo de la fase

Clasificar cada uno de los 27 atributos propios del log como elegible o no elegible para un modelo que predice en t0. La clasificación separa cuatro preguntas: si el atributo tiene valor en t0 (D11a), si tiene cobertura suficiente (D11d), qué tipo de circularidad presenta si la tiene (D11b) y si la marca de tiempo es fiel al momento real de captura (D11c, pendiente). En esta fase no se entrena ningún modelo. Objetivo: identificar la naturaleza y el tipo de circularidad en las variables centrales del estudio, lo que fundamenta la comparación entre el modelo base (con circularidad) y el modelo corregido.

## 2. Glosario

| Término | Definición |
|---|---|
| **ER (Emergency Room)** | Servicio de urgencias. Es el punto de entrada del paciente al hospital. |
| **Clasificación de gravedad** | Clasificación rápida de la gravedad al llegar, para decidir la prioridad de atención. |
| **SIRS** | Criterios clínicos de respuesta inflamatoria sistémica (temperatura, frecuencia cardiaca, respiratoria y leucocitos). Se usan para identificar sepsis. |
| **UCI (IC)** | Unidad de cuidados intensivos. El evento `Admission IC` registra el ingreso a esta unidad. Es el desenlace que predice la tesis. |
| **NC** | Unidad de cuidado normal (sala general). `Admission NC` no es desenlace positivo. |
| **t0** | Momento de la predicción. Aquí es la marca de `ER Registration`. Solo puede usarse información con marca ≤ t0. |
| **t_ic** | Marca de `Admission IC`. Existe solo en los 110 casos positivos. |
| **Caso positivo / negativo** | Positivo: tiene `Admission IC` (110). Negativo: no lo tiene (940). |
| **Disponibilidad en t0** | Porcentaje de casos con al menos un valor del atributo con marca ≤ t0. |
| **Diferencia en puntos porcentuales (pp)** | Disponibilidad en positivos menos disponibilidad en negativos. Indica si la falta del dato se relaciona con el desenlace. |
| **IC 95 %** | Intervalo que, con 95 % de confianza, contiene el valor real de una diferencia. Si incluye 0, la diferencia puede deberse al azar. |
| **Cardinalidad** | Número de categorías distintas de una variable categórica. |
| **Categoría de ausencia** | Categoría explícita de "sin valor registrado". No se sustituye por el valor más frecuente. |
| **Empate temporal** | Dos o más eventos del mismo caso con la misma marca de tiempo. |
| **Booleano** | Variable de presencia o ausencia de una condición. Aquí, una celda vacía significa "no registrado". |
| **Captura tardía** | Registro de un dato después del momento en que debió estar disponible. |
| **Circularidad definicional** | El atributo define parte del desenlace. |
| **Circularidad temporal** | El atributo se registra después del desenlace. |
| **Proxy** | El atributo sustituye al desenlace y no lo define. |
| **Fuga de información** | Uso, en el entrenamiento o la evaluación, de información que no existe al momento de predecir. Produce métricas infladas. |

## 3. Avance validado

| Elemento | Resultado | Script |
|---|---|---|
| Casos con exactamente un `ER Registration` | 1,050 de 1,050 | `fase2_ventanas_t0.py` |
| Casos con `Admission IC` anterior a t0 | 0 | `fase2_ventanas_t0.py` |
| Casos sin primer evento en `ER Registration` | 55; su registro está en las posiciones 1 a 5 | `fase2_diagnostico_t0.py` |
| Disponibilidad en t0 de `Age`, booleanos y criterios SIRS | 100 % en ambas clases; diferencia 0 | `fase2_disponibilidad_t0.py` |
| Disponibilidad en t0 de `Diagnose` | 98.2 % positivos; 73.2 % negativos; diferencia 24.99 pp | `fase2_disponibilidad_t0.py` |
| Disponibilidad en t0 de `CRP`, `LacticAcid`, `Leucocytes` | 5.5 %, 0.9 % y 4.6 % en positivos | `fase2_disponibilidad_t0.py` |
| Cardinalidad de `Diagnose` | 145 códigos; 14 con ≥ 10 casos (525 casos); 84 con un solo caso | `fase2_cardinalidad_diagnose.py` |

## 4. Resultados de la sesión del 31 de octubre

### 4.1 Mecanismo de ausencia de `Diagnose`

- 254 casos no tienen `Diagnose` en t0. Ninguno lo tiene en un momento posterior. Todos son del mecanismo A (nunca registrado).
- 43 registros tienen marca anterior a `ER Registration`. Es una anomalía que la fuente debe explicar.
- Mecanismo C (actividad con la misma marca): en 780 registros no hay otra actividad con esa marca. El resto coincide con `CRP` (12), `Leucocytes` (4) y `LacticAcid` (1). Cifra provisional; ver sección 5.

### 4.2 Registro de `Diagnose` según clase

- 796 registros: 108 en positivos y 688 en negativos.
- Los 796 tienen marca ≤ t0. Ningún registro tiene marca posterior a t0.

### 4.3 Diferencia de disponibilidad

- `Diagnose`: 24.99 pp. Intervalo IC 95 % aproximado de 21 a 29 pp (cálculo con error estándar de la diferencia de proporciones, ≈ 0.019). Supera R1.
- Booleanos, criterios SIRS y `Age`: diferencia 0. No activan R1.
- `CRP`, `LacticAcid` y `Leucocytes`: diferencias de 3.75, 0.70 y 2.10 pp. No activan R1, pero su cobertura en t0 es menor a 6 %, así que D11d los excluye.

## 5. Correcciones de la semana

1. La tabla de faltantes de la Fase 1 sobreestimaba la disponibilidad en t0, porque usaba el primer valor no nulo por columna (D6). El inventario temporal lo corrigió.
2. Se afirmó que los 55 valores booleanos estaban después de t0. Están en `ER Registration`, que no era el primer evento de esos casos.
3. Se afirmó que CRP, LacticAcid y Leucocytes quedaban excluidos por D11a. Con el criterio escrito, tienen 22, 3 y 28 casos elegibles. Su exclusión se justifica con D11d.
4. La columna `ventana_predictiva` se renombró a `post_t0_pre_IC`.
5. **Conteo del mecanismo C.** Se reportó "16 restantes", pero los conteos suman 17. La tabla total suma 797 frente a 796 registros, porque el cruce duplicó un registro que coincidía con dos actividades. Corrección pendiente en el script: contar registros únicos.
6. **Prueba de "más de un código por caso".** Se describió como evidencia de que `Diagnose` es constante dentro del caso. Es incorrecta: cada caso tiene a lo sumo un registro, así que la prueba da 0 por construcción.
7. **Prueba de "diagnósticos posteriores a UCI".** Se describió como evidencia de ausencia de captura retrospectiva. No lo es: la columna no tiene registros posteriores a t0 en ningún caso, así que la prueba no podía detectar captura tardía.

## 6. Decisiones

**D9 (validada).** t0 = marca de `ER Registration`.
*Concepto:* el registro en urgencias es el momento en que el clínico tiene información de entrada sin conocer el desenlace.
*Razón:* lo define el README y se cumple en 1,050 de 1,050 casos.

**D10 (validada para booleanos y SIRS; pendiente para laboratorios y `Diagnose`).** Una celda vacía significa "no registrado al momento considerado".
*Concepto:* "no registrado" no equivale a "falso" ni a "normal". Convertir el vacío en 0 introduce un supuesto clínico no documentado.
*Razón:* en booleanos y SIRS no hay vacíos en t0, así que no altera su clasificación.

**D11a (propuesta).** Elegibilidad temporal: el atributo es elegible si tiene al menos un valor con marca ≤ t0.
*Concepto:* criterio basado solo en el tiempo. No usa la clase del desenlace.
*Razón:* si la selección de variables usara la clase, la comparación entre modelos quedaría contaminada.
*Limitación:* no garantiza que la marca sea fiel al momento real de captura. Eso corresponde a D11c.

**D11b (propuesta).** Tipo de circularidad: temporal (registrado después de `Admission IC`), definicional o proxy.
*Concepto:* explica por qué un atributo no es válido.
*Estado:* la circularidad temporal se verifica con datos. La definicional y la proxy requieren documentación.

**D11c (pendiente de fuente).** La marca de tiempo es necesaria pero no suficiente.
*Concepto:* un valor puede tener marca ≤ t0 y haberse capturado después de la decisión de ingreso (captura retrospectiva). Si ocurre, el atributo se excluye aunque cumpla D11a.
*Evidencia de datos disponible:*
- `Diagnose` no tiene ningún registro posterior a t0. Puede ser una captura única al llegar, o un dato que nunca se actualiza.
- 43 registros tienen marca anterior a `ER Registration`.
- Hay registros de `Diagnose` con la misma marca que `CRP`, `Leucocytes` o `LacticAcid`.
*Lo que los datos no pueden decidir:* si el valor se registró al llegar o se completó después con una marca retroactiva.
*Criterio de cierre:* una cita documental que indique el momento de captura de `Diagnose`.
*Estado actual:* `Diagnose` se mantiene como candidato, no como elegible definitivo.

**D11d (propuesta, umbral fijado después de ver los datos).** Cobertura mínima: un atributo con disponibilidad en t0 menor a 50 % no entra como predictor principal.
*Concepto:* un predictor que falta en la mayoría de los pacientes al momento de la predicción no sirve en urgencias.
*Declaración:* el umbral se propuso después de revisar la tabla. Se verificará con un análisis de sensibilidad al 95 %.

**D12 (propuesta).** La partición de entrenamiento y prueba se hace por caso, y la imputación y la selección se ajustan solo dentro de cada partición de entrenamiento.
*Concepto:* evita que el mismo paciente aparezca en entrenamiento y prueba, y que la selección use información de prueba.
*Observación:* si todas las variables son de t0, cada caso aporta una sola fila, y la partición por caso se cumple de forma automática. El riesgo aparece solo si entran valores posteriores a t0.

**D13 (pendiente).** Tiempo de referencia común para positivos y negativos.
*Concepto:* los negativos permanecen más tiempo hospitalizados y acumulan más registros. Esa asimetría puede producir diferencias artificiales aunque ningún valor sea circular.
*Estado:* se definirá solo si la justificación de excluir laboratorios lo requiere.

**D14 (nueva, pendiente de validación con la asesora).** Definición de los dos modelos que se comparan.
*Concepto:*
- Modelo base: usa todos los atributos tal como aparecen en el log, incluidos los valores posteriores a t0.
- Modelo corregido: usa solo los atributos que cumplen D11a, D11d y, cuando se cierre, D11c.
*Razón:* el objetivo es medir cuánto cambia el desempeño al excluir la circularidad. Si el modelo base ya excluyera lo circular, no habría diferencia que medir.

**R1 (aplicada).** Se marca un atributo si el IC 95 % de la diferencia no incluye 0 y la diferencia absoluta es ≥ 5 pp.
*Resultado:* se activa en `Diagnose`. No se activa en booleanos, SIRS ni laboratorios.
*Nota:* se fijó antes de revisar la tabla de disponibilidad por clase.

**R2 (aplicada).** Categorías de `Diagnose` con menos de 10 casos se agrupan en "otra". La ausencia es una categoría propia.
*Resultado:* 14 categorías frecuentes, "otra" (271 casos) y "sin diagnóstico en t0" (254 casos).
*Nota:* se fijó antes de revisar el resultado de cardinalidad.

## 7. Preguntas para la fuente

Estas preguntas no se responden con los datos. Deben buscarse en la documentación del log (4TU.ResearchData, DOI del README) y en Mannhardt y Blinde (2017). Cada respuesta debe registrarse con su cita y página.

**Sobre `Diagnose`**
1. ¿Cuándo se captura `Diagnose`: al llegar, durante la clasificación de gravedad o después de decidir el ingreso?
2. ¿Por qué ningún caso tiene un registro de `Diagnose` posterior a t0?
3. ¿Por qué 43 registros tienen marca anterior a `ER Registration`?
4. ¿Es una impresión clínica inicial o un diagnóstico confirmado después?
5. ¿Qué significan los códigos `C` (147 casos), `B` (82) y `E` (67)?

**Sobre las marcas de tiempo**
6. ¿`ER Registration` marca la llegada del paciente o su admisión administrativa?
7. ¿Por qué `IV Liquid` e `IV Antibiotics` aparecen antes de `ER Registration` en algunos casos? ¿Es la hora de captura o la del evento?
8. ¿Cómo se ordenan los eventos con la misma marca exacta?

**Sobre el desenlace**
9. ¿Qué criterio clínico define `Admission IC`, y en qué momento exacto se registra?
10. ¿Qué diferencia y qué criterio separa `Admission NC` de `Admission IC`?

**Sobre los atributos**
11. ¿Qué significa `DiagnosticIC`? Se registra en t0 en 848 casos positivos y negativos por igual.
12. ¿Los criterios SIRS y los indicadores de gravedad forman parte de la clasificación de gravedad, según Mannhardt y Blinde (2017)?
13. ¿Qué relación hay entre `LacticAcid` (valor) y `DiagnosticLacticAcid` (indicador de solicitud)?
14. ¿Por qué el log documenta 39 atributos y el archivo contiene 27 propios?
15. ¿Una celda vacía en un booleano significa "no registrado" o "falso"?

**Preguntas para la asesora**
- ¿Validar D14 como definición de los modelos base y corregido?
- ¿Aceptar el umbral de 50 % de D11d con sensibilidad al 95 %?
- ¿Cómo tratar un atributo con circularidad documentada pero disponible en t0 (proxy)?
- ¿Aceptar D11c como criterio aunque la documentación no responda la pregunta 2?

## 8. Siguientes pasos

**Antes de cerrar la Fase 2**
1. Corregir `fase2_ausencia_diagnose.py` para contar registros únicos y recalcular el mecanismo C.
2. Buscar en la fuente las preguntas de la sección 7 y registrar cada cita.
3. Cerrar D10, D11b y D11c con evidencia documental.
4. Construir la tabla final de los 27 atributos con estas columnas: atributo, cobertura en t0, diferencia en pp, D11a, D11d, tipo de circularidad (D11b), decisión y cita.
5. Ejecutar el análisis de sensibilidad de D11d con 95 %.
6. Validar D14 con la asesora.
7. Decidir D13 solo si la exclusión de laboratorios la requiere.
8. Parametrizar `publicar_semana.sh` por semana, para que no reejecute los scripts de la Fase 1 dentro de otra carpeta.

**Para la Fase 3 (no iniciar sin cerrar la Fase 2)**
- Pipelines en scikit-learn con imputación y escalado dentro del pipeline, ajustados solo en el entrenamiento de cada partición.
- XGBoost con valores faltantes nativos. Regresión logística con imputación y escalado. Random Forest con imputación, verificando el comportamiento de la versión instalada.
- Validación cruzada anidada. Métrica principal: área bajo la curva precisión-recall. Recall reportado en un umbral fijado antes de los experimentos.
- Selección de máximo 10 variables (OE2) a partir del conjunto elegible, con un criterio declarado antes de entrenar. No se usa la clase para elegir atributos.

## 9. Registro de la sesión

- Publicado en GitHub: commit `8cca4f4`, avance de Fase 2 (validación de t0, disponibilidad por clase y cardinalidad).
- Pendiente de publicación: scripts `fase2_ausencia_diagnose.py` y `fase2_dx_vs_ic.py`, sus resultados, esta bitácora y la actualización de `publicar_semana.sh`.

## 10. Registro de actualización (2 al 13 de noviembre de 2026)

### 10.1 Métricas de la semana

| Indicador | Valor | Cómo se obtuvo |
|---|---|---|
| Commits desde el 2 de noviembre | 7 | `git log --since=2026-11-02` |
| Scripts de la Fase 2 | 7 | `scripts/fase2_*.py` |
| Archivos de resultados generados | 9 | carpeta `resultados/` |
| Decisiones registradas | 9 (D9 a D14, con D11a a D11d) | sección 4 |
| Reglas de revisión fijadas antes de ver resultados | 2 (R1 y R2) | sección 4 |
| Correcciones registradas | 7 | sección 5 |
| Preguntas para la fuente | 15 | sección 7 |

### 10.2 Cambios respecto al 31 de octubre

- t0 se redefinió como la marca de `ER Registration` (D9). Antes se tomaba el primer evento de cada caso.
- La tabla de disponibilidad por clase se recalculó con la nueva definición de t0.
- El conteo del mecanismo C se corrigió a registros únicos: 796 registros, sin duplicados.
- La columna `ventana_predictiva` se renombró a `post_t0_pre_IC`.

### 10.3 Mejoras metodológicas

- Se separó la elegibilidad temporal (D11a) de la fidelidad de la captura (D11c), que queda pendiente de documentación.
- Se fijó el umbral de cobertura (D11d) y las reglas R1 y R2 antes de revisar los resultados, y se declaró que el umbral de 50 % se propuso después de ver los datos.
- Los scripts verifican sus supuestos con `assert`, y las ediciones se respaldan antes de modificarse.

### 10.4 Nuevas aportaciones

- Definición de la investigación como procedimiento metodológico, en la sección de Conveniencia del documento de planteamiento.
- Lista de referencias en APA 7 para el documento de planteamiento.
- Documento de planteamiento, versión 3, para la entrega de esta semana.
- Propuesta de archivo de tracking visual del proyecto, pendiente de publicación.

### 10.5 Pendientes al cierre

- Cerrar D11c con evidencia documental sobre el momento de captura de `Diagnose`.
- Definir D13 solo si la exclusión de laboratorios lo requiere.
- Validar D14 con el asesor antes de la Fase 3.
- Responder las preguntas de la sección 7, empezando por las relacionadas con `Diagnose` y `Admission IC`.
