# Semana del 2 de noviembre de 2026: Fase 2, clasificación de atributos

**Autora:** Jessica Melani Romero Lora
**Proyecto:** Detección y exclusión de variables circulares en modelos de ingreso a UCI
**Fase:** 2 de 4 (auditoría temporal, OE1)
**Estado:** en curso

## 1. Objetivo de la semana

Clasificar cada atributo propio del log como elegible o no elegible para un modelo de predicción en t0. La clasificación separa dos preguntas: si el atributo está disponible en t0 (criterio temporal) y, si no lo está, por qué (tipo de circularidad). No se entrena ningún modelo en esta semana.

## 2. Glosario de términos nuevos

| Término | Definición |
|---|---|
| **t0** | Momento de la predicción. En este estudio es la marca de tiempo de `ER Registration` (registro en urgencias). Solo la información con marca ≤ t0 puede usarse como predictor. |
| **t_ic** | Marca de tiempo del evento `Admission IC` (ingreso a UCI). Existe solo en los 110 casos positivos. |
| **Caso positivo / negativo** | Positivo: el caso tiene `Admission IC` (110). Negativo: no lo tiene (940). |
| **Disponibilidad en t0** | Proporción de casos que tienen al menos un valor del atributo con marca ≤ t0. |
| **Diferencia en puntos porcentuales (pp)** | Disponibilidad en t0 de positivos menos la de negativos. Mide si la falta del dato está relacionada con el desenlace. |
| **Intervalo de confianza al 95 % (IC 95 %)** | Rango en el que, con 95 % de confianza, se ubica el valor real de una diferencia. Si incluye 0, la diferencia puede deberse al azar. |
| **Cardinalidad** | Número de categorías distintas de una variable categórica. |
| **Categoría de ausencia** | Categoría explícita que significa "sin valor registrado", en lugar de imputar el valor más frecuente. |
| **Empate temporal** | Dos o más eventos del mismo caso con la misma marca de tiempo. Su orden depende del archivo. |
| **Booleano** | Variable de presencia o ausencia de una condición. En este log, una celda vacía significa "no registrado". |
| **Captura tardía** | Registro de un dato después del momento en que debió estar disponible. Puede tener una marca de tiempo anterior a su captura real. |

## 3. Avance validado

| Elemento | Resultado | Script |
|---|---|---|
| Casos con exactamente un `ER Registration` | 1,050 de 1,050 | `fase2_ventanas_t0.py` |
| Casos con `Admission IC` anterior a t0 | 0 | `fase2_ventanas_t0.py` |
| Eventos simultáneos a t0 (distintos de `ER Registration`) | 0 | `fase2_ventanas_t0.py` |
| Casos sin primer evento en `ER Registration` | 55 (su registro está en las posiciones 1 a 5) | `fase2_diagnostico_t0.py` |
| Disponibilidad en t0 de booleanos, criterios SIRS y `Age` | 100 % en ambas clases, diferencia 0 | `fase2_disponibilidad_t0.py` |
| Disponibilidad en t0 de `Diagnose` | 98.2 % positivos, 73.2 % negativos, diferencia 25.0 pp | `fase2_disponibilidad_t0.py` |
| Disponibilidad en t0 de `Leucocytes`, `CRP`, `LacticAcid` | 4.6 %, 5.5 % y 0.9 % en positivos | `fase2_disponibilidad_t0.py` |
| Cardinalidad de `Diagnose` con t0 | 145 códigos; 14 con ≥ 10 casos (525 casos); 84 con un solo caso | `fase2_cardinalidad_diagnose.py` |

## 4. Decisiones

**D9 (revisada, validada).** t0 = marca de `ER Registration`.
*Concepto:* el registro en urgencias es el momento en que el clínico tiene información de entrada sin conocer el desenlace.
*Razón:* lo define el README; se cumple en 1,050 de 1,050 casos.

**D10 (validada para booleanos y SIRS; pendiente para laboratorios y `Diagnose`).** Una celda vacía significa "no registrado al momento considerado".
*Concepto:* no es lo mismo "no registrado" que "falso" o "normal". Convertir el vacío en 0 introduce un supuesto clínico sin documentar.
*Razón:* en los booleanos no hay vacíos en t0, así que no altera su clasificación.

**D11a (propuesta).** Elegibilidad temporal: un atributo es elegible si tiene al menos un valor con marca ≤ t0.
*Concepto:* criterio basado solo en el tiempo. No usa la clase del desenlace, para evitar que la selección de variables contamine la comparación entre modelos.
*Limitación:* no garantiza que la marca sea fiel al momento real de captura. Esa verificación corresponde a D11c.

**D11b (propuesta).** Tipo de circularidad: temporal (registrado después de `Admission IC`), definicional (define el desenlace) o proxy (sustituye al desenlace).
*Concepto:* clasifica la razón por la que un atributo no es válido. La circularidad temporal se verifica con datos; la definicional y la proxy requieren documentación.

**D11c (nueva, pendiente de fuente).** La marca de tiempo es necesaria pero no suficiente.
*Concepto:* un valor puede tener marca ≤ t0 y haber sido capturado después de la decisión de ingreso a UCI (captura retrospectiva). En ese caso se excluye, aunque D11a lo acepte.
*Razón:* la marca no tiene anotaciones posteriores al ingreso, así que la fidelidad del registro no puede verificarse solo con los datos. La documentación del log debe confirmarlo.

**D11d (nueva, umbral propuesto después de ver los datos).** Cobertura mínima: un atributo con disponibilidad en t0 menor a 50 % no entra como predictor principal.
*Concepto:* un predictor que falta en la mayoría de los pacientes en el momento de la predicción no es útil en urgencias.
*Declaración:* el umbral de 50 % se fijó después de ver la tabla. Como verificación, se repetirá el análisis con 95 % y se comprobará si la conclusión cambia.

**D13 (nueva, sin definir).** Tiempo de referencia común para positivos y negativos.
*Concepto:* los negativos permanecen más tiempo en el hospital y tienen más oportunidad de acumular registros. Esa asimetría puede generar diferencias artificiales aunque ningún valor sea circular.
*Pendiente:* definir una ventana común antes de comparar disponibilidad en laboratorios.

**R1 (aplicada).** Regla de revisión de diferencias: marcar un atributo si el IC 95 % de la diferencia no incluye 0 y la diferencia absoluta es ≥ 5 pp.
*Concepto:* evita interpretar diferencias pequeñas que puedan deberse al azar, dado el tamaño de 110 positivos.
*Resultado:* se activa en `Diagnose` (25.0 pp). No se activa en booleanos, criterios SIRS ni laboratorios.
*Nota:* se fijó antes de revisar la tabla de disponibilidad por clase.

**R2 (aplicada).** Agrupación de la cardinalidad: categorías con menos de 10 casos se agrupan en "otra". La ausencia de `Diagnose` es una categoría propia.
*Concepto:* las categorías con muy pocos casos no permiten estimar un efecto estable y aumentan el riesgo de sobreajuste.
*Resultado:* 14 categorías frecuentes, "otra" (271 casos) y "sin diagnóstico en t0".
*Nota:* se fijó antes de revisar el resultado de cardinalidad.

## 5. Correcciones de la semana

1. La tabla de faltantes de la Fase 1 sobreestimaba la disponibilidad en t0, porque usaba el primer valor no nulo por columna (D6). El inventario temporal lo corrigió.
2. Se afirmó que los 55 valores booleanos estaban después de t0. La comprobación mostró que están en `ER Registration`, que no era el primer evento de esos casos.
3. Se afirmó que CRP, LacticAcid y Leucocytes quedaban excluidos por D11a. Eso era incorrecto: con el criterio tal como está escrito tienen 22, 3 y 28 casos elegibles. Su exclusión se justifica con D11d.
4. La columna `ventana_predictiva` tenía un nombre engañoso; se renombró a `post_t0_pre_IC`.

## 6. Preguntas abiertas para la fuente

Estas preguntas no pueden responderse con los datos. Deben buscarse en la documentación del log (4TU.ResearchData, DOI en el README del repositorio) y en Mannhardt y Blinde (2017).

1. ¿Qué significa la ausencia de `Diagnose` en un caso: no se formuló diagnóstico, o no se registró?
2. ¿En qué momento se captura `Diagnose`: al llegar, durante el triaje o después de decidir el ingreso? Esto determina si D11c aplica.
3. ¿Por qué 43 registros de `Diagnose` tienen marca anterior a `ER Registration`?
4. ¿`Diagnose` es una impresión clínica inicial o un diagnóstico confirmado posteriormente?
5. ¿Qué significa `DiagnosticIC`? Su nombre sugiere relación con la UCI, pero aparece en t0 en 1,050 casos.
6. ¿Qué criterio define `Admission IC` y en qué momento exacto se registra?
7. ¿`ER Registration` marca la llegada del paciente o su admisión administrativa?
8. ¿Los criterios SIRS y los indicadores de gravedad forman parte del triaje, según Mannhardt y Blinde (2017)?
9. ¿Qué significa el código `C` de `Diagnose`, que aparece en 147 casos?
10. ¿Por qué el log documenta 39 atributos y el archivo contiene 27 propios?

## 7. Pendientes para la próxima sesión

- Ejecutar `fase2_ausencia_diagnose.py` para identificar el mecanismo de ausencia de `Diagnose` (A, B o C).
- Buscar en la documentación las preguntas 1 a 10 y registrar la respuesta con su cita.
- Cerrar D10, D11b y D11c con evidencia documental.
- Definir D13 antes de comparar disponibilidad de laboratorios.
- Clasificar los booleanos y los criterios SIRS según el resultado de D11b.# Semana del 2 de noviembre de 2026: Fase 2, clasificación de atributos

**Fase:** 2 de 4 (auditoría temporal, OE1)
**Estado de la semana:** en curso

## 1. Avance validado

| Elemento | Evidencia |
|---|---|
| t0 = `ER Registration` (D9 revisada) | 1,050 de 1,050 casos con exactamente un registro (`fase2_ventanas_t0.py`) |
| Admission IC previo a t0 | 0 casos |
| Booleanos y criterios SIRS disponibles en t0 | 1,050 de 1,050 casos |
| Origen de los 55 casos sin primer evento en `ER Registration` | Su registro ocurre en las posiciones 1 a 5 (`fase2_diagnostico_t0.py`) |

## 2. Correcciones registradas

- La tabla de faltantes de la Fase 1 sobreestimaba la disponibilidad en t0, porque usaba el primer valor no nulo por columna (decisión D6). Se corrigió con el inventario temporal.
- Se afirmó que los 55 valores booleanos estaban después de t0. La comprobación mostró que están en `ER Registration`, que no era el primer evento de esos casos.
- La columna `ventana_predictiva` tenía un nombre engañoso; se renombró a `post_t0_pre_IC`.

## 3. Propuestas pendientes de evidencia

| # | Propuesta | Estado |
|---|---|---|
| D10 | Celda vacía = no registrado al momento considerado. | Pendiente de cierre |
| D11a | Elegible si tiene un valor con marca ≤ t0. Decisión basada solo en el tiempo, sin usar la clase. | Pendiente de cierre |
| D11b | Tipo de circularidad (temporal, definicional, proxy), con evidencia documental. | Pendiente de cierre |
| R1 | Revisión de `diferencia_pp`: IC 95 % que no incluya 0 y diferencia ≥ 5 puntos. | Fijada antes de ver resultados |
| R2 | Categorías de `Diagnose` con menos de 10 casos se agrupan en "otra". | Fijada antes de ver resultados |

## 4. Preguntas abiertas para la fuente

1. ¿Qué significa `DiagnosticIC` y cuándo se registra?
2. ¿Qué criterio define `Admission IC`?
3. ¿`ER Registration` marca llegada o admisión administrativa?
4. ¿Por qué 43 valores de `Diagnose` tienen marca anterior a t0?
5. ¿`Diagnose` es impresión inicial o diagnóstico confirmado después?
6. ¿Los criterios SIRS forman parte del triaje?
7. ¿Por qué 39 atributos documentados frente a 27 propios?

