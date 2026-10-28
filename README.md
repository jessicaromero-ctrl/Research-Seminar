<div align="center">

# Detección y exclusión de variables circulares en modelos de ingreso a UCI

### Un procedimiento sobre logs de eventos clínicos con aprendizaje automático y minería de procesos

**Universidad Politécnica Metropolitana del Estado de Hidalgo**

**Maestría en Inteligencia Artificial · Seminario de Investigación**

**Autora:** Jessica Melani Romero Lora · *25322116@upmh.edu.mx*
**Director de tesis:** Dr. Marcos Yamir Gómez

**Versión:** 0.5 · **Estado:** en construcción · **Fecha:** octubre de 2026

![Estado](https://img.shields.io/badge/estado-en%20construcci%C3%B3n-orange) ![Datos](https://img.shields.io/badge/datos-p%C3%BAblicos%20desidentificados-blue)

</div>

---

## Resumen

La presente investigación estudia en qué medida la exclusión de **variables circulares** modifica el desempeño predictivo de un modelo de **ingreso a la unidad de cuidados intensivos (UCI)** construido sobre un log de eventos clínicos de pacientes con sospecha de sepsis. Se entiende por variable circular aquella que contiene información del propio desenlace, ya sea porque lo define, porque se registra después de él o porque actúa como un *proxy* fuerte. Dicha información no está disponible en el momento de la predicción y, cuando se incorpora al modelo, sobreestima el desempeño reportado.

El procedimiento propuesto integra tres componentes: (1) la **minería de procesos**, para ubicar cada variable en la traza respecto al ingreso a UCI; (2) el **aprendizaje automático**, para comparar un modelo base con un modelo corregido; y (3) la **validación con fugas inyectadas**, para estimar la precisión y el recall del procedimiento de detección. El caso de estudio es el log público *Sepsis Cases* (Mannhardt, 2016), con 1,050 casos de un hospital de Países Bajos.

**Palabras clave:** fuga de información, variables circulares, minería de procesos, sepsis, unidad de cuidados intensivos, validación cruzada anidada.

**Documentos del repositorio:**

| Archivo | Contenido |
|---|---|
| [`Protocolo V5.pdf`](Protocolo%20V5.pdf) | Protocolo breve de investigación (versión 5) |
| [`Estado_del_Arte_v3.xlsx`](Estado_del_Arte_v3.xlsx) | Matriz del estado del arte: referentes, marco teórico y relación con los objetivos |
| [`Estado_del_Arte.xlsx`](Estado_del_Arte.xlsx) | Versión de la matriz con enlaces adicionales a las fuentes |
| [`LICENSE`](LICENSE) | Archivo de licencia del repositorio |

> **Aviso.** Este repositorio documenta un prototipo de investigación en construcción: los objetivos, el diseño y las referencias pueden cambiar, y ninguna cifra es un resultado final. El log analizado es público y está desidentificado por su fuente; el repositorio no contiene copia de los datos, no utiliza datos institucionales ni de terceros y prohíbe cualquier intento de reidentificación.

---

## Tabla de contenido

1. [Estado del arte](#1-estado-del-arte)
2. [Planteamiento del problema](#2-planteamiento-del-problema)
3. [Pregunta de investigación con los 8 elementos](#3-pregunta-de-investigación-con-los-8-elementos)
4. [Objetivo general](#4-objetivo-general)
5. [Objetivos específicos](#5-objetivos-específicos)
6. [Justificación](#6-justificación)
7. [Relevancia social](#7-relevancia-social)
8. [Conveniencia](#8-conveniencia)
9. [Valor teórico](#9-valor-teórico)
10. [Implicaciones prácticas](#10-implicaciones-prácticas)
11. [Hipótesis de investigación e hipótesis nula](#11-hipótesis-de-investigación-e-hipótesis-nula)
12. [Marco teórico](#12-marco-teórico)
13. [Temas del marco teórico](#13-temas-del-marco-teórico)
14. [Referencias](#referencias)

---

## 1. Estado del arte

La revisión de la literatura se sistematizó en la matriz [`Estado_del_Arte_v3.xlsx`](Estado_del_Arte_v3.xlsx), que registra para cada referente el año, la fuente, el país, el tema, el objetivo específico con el que se relaciona, su aporte a la investigación y su estado de verificación. La matriz reúne **46 referentes**, de los cuales 28 se han verificado contra la fuente original y 18 permanecen pendientes de verificación.

| Tema (clasificación de la matriz) | Referentes |
|---|---|
| Minería de procesos | 20 |
| Fuga de información | 10 |
| Validación de modelos | 6 |
| Sepsis / contexto clínico | 4 |
| Datos sintéticos | 2 |
| Otro (calidad de datos y algoritmos) | 4 |
| **Total** | **46** |

| Objetivo relacionado | Referentes |
|---|---|
| OE1 | 14 |
| OE2 | 9 |
| OE3 | 4 |
| Marco general | 19 |

La literatura revisada se organiza en dos grandes líneas que, hasta ahora, se han desarrollado de forma mayormente independiente.

**1.1 Minería de procesos en salud y sepsis.** Las revisiones de Rojas et al. (2016) y de Aversano et al. (2025) documentan el uso creciente de la minería de procesos en contextos hospitalarios para describir trayectorias de pacientes, verificar la conformidad con guías clínicas y detectar cuellos de botella. En el dominio específico de la sepsis, Mannhardt y Blinde (2017) analizaron las trayectorias de 1,050 pacientes de un hospital neerlandés, desde el registro en urgencias hasta el alta, con un log enriquecido con resultados de laboratorio y listas de verificación de triaje; su trabajo muestra que la minería de procesos permite esclarecer el flujo de pacientes y contrastarlo con las guías clínicas. Trabajos posteriores sobre rutas clínicas de sepsis (Quintano Neira et al., 2020; Silva Júnior et al., 2023) y sobre metodologías de proyectos de minería de procesos en hospitales (Rebuge y Ferreira, 2012; Pereira et al., 2020) aportan procedimientos replicables para delimitar el proceso y leer el orden de las actividades. Esta línea, sin embargo, se centra en el descubrimiento y la conformidad del proceso, y no utiliza el orden de la traza para decidir qué variables son legítimas como predictores.

**1.2 Fuga de información en aprendizaje automático.** Kaufman et al. (2011) formalizaron la fuga de información (*leakage*) en minería de datos y propusieron estrategias para detectarla y evitarla. Kapoor y Narayanan (2023) documentaron que la fuga afecta al menos a 294 artículos en 17 disciplinas, propusieron una taxonomía de ocho tipos de fuga y mostraron que, al corregirla, modelos complejos reportados como superiores dejan de aventajar sustancialmente a métodos estadísticos más simples. Sasse et al. (2025) presentan una revisión de los escenarios de fuga en aprendizaje supervisado, mientras que Rosenblatt et al. (2024) cuantificaron empíricamente que la fuga por selección de variables y por sujetos repetidos infla el desempeño de los modelos predictivos. En el plano metodológico, Kriegeskorte et al. (2009) definieron el análisis circular (*double dipping*) y Cawley y Talbot (2010) demostraron el sesgo optimista que surge cuando la selección del modelo no está anidada en la evaluación. Respecto a la detección automática, Yang et al. (2022) desarrollaron un análisis estático para detectar fugas en cuadernos (*notebooks*) de ciencia de datos, y Alomar et al. (2025) propusieron una herramienta de código abierto con el mismo fin. Estas herramientas detectan errores en el código del *pipeline*, pero no evalúan si una variable es circular por su posición temporal respecto al desenlace.

**1.3 Vacío identificado.** Ninguno de los referentes revisados combina el orden temporal que ofrece un log de eventos con la detección de variables circulares en un modelo predictivo clínico, ni valida esa detección frente a fugas de intensidad conocida. La presente investigación se sitúa en esa intersección.

*Pendiente del estado del arte:* documentar la estrategia de búsqueda (bases de datos, cadenas de búsqueda, fechas y criterios de inclusión) y concluir la verificación bibliográfica de los 18 referentes marcados como pendientes.

---

## 2. Planteamiento del problema

En contextos clínicos, los modelos predictivos que anticipan el ingreso a una unidad de cuidados intensivos se proponen como herramientas de apoyo para el triaje y la asignación de recursos. Sin embargo, el desempeño reportado de estos modelos puede estar inflado por la inclusión de **variables circulares**: aquellas que contienen información del propio desenlace que se intenta predecir. Una variable puede ser circular por tres vías:

| Tipo de circularidad | Descripción |
|---|---|
| **Definicional** | La variable define operacionalmente el desenlace. |
| **Temporal** | La variable se registra después del evento de interés y, por lo tanto, no está disponible en el momento de la predicción. |
| **Proxy** | La variable actúa como un sustituto fuerte del desenlace. |

Un modelo entrenado con estas variables mide, en parte, su propia consecuencia y no su capacidad predictiva real, lo que puede conducir a decisiones clínicas basadas en métricas que no reflejan el desempeño en la práctica (Kapoor y Narayanan, 2023; Kaufman et al., 2011).

Este problema, conocido en la literatura como fuga de información, es difícil de detectar en conjuntos de datos tabulares convencionales, en los que se desconoce el momento en que se registró cada atributo. En cambio, los **logs de eventos clínicos** documentan el orden de las actividades y sus marcas de tiempo, por lo que permiten determinar de manera sistemática si una variable se registró antes o después del ingreso a UCI. No obstante, ese orden rara vez se emplea en la selección de predictores.

En consecuencia, el problema que aborda esta investigación es doble:

1. desarrollar un procedimiento que detecte variables circulares a partir del orden temporal de las trazas de eventos; y
2. cuantificar en qué medida la exclusión de dichas variables modifica el desempeño de un modelo de predicción del ingreso a UCI, con el fin de estimar cuánto había inflado la circularidad las métricas reportadas.

El estudio se delimita al log *Sepsis Cases* (Mannhardt, 2016), que contiene 1,050 casos, 15,214 eventos y 16 actividades registrados en un hospital de Países Bajos entre noviembre de 2013 y junio de 2015. El desenlace es el ingreso a UCI (actividad `Admission IC`), presente en 110 casos (cerca del 10 %). La predicción se realiza con los atributos del primer evento (registro en urgencias). La documentación oficial del log reporta 39 atributos, mientras que el archivo analizado contiene 27 atributos propios; el estudio trabaja con estos 27 y declara la diferencia como limitación.

---

## 3. Pregunta de investigación con los 8 elementos

> **¿En qué medida la exclusión de variables circulares influye en el desempeño predictivo del ingreso a UCI, en el log *Sepsis Cases* de un hospital de Países Bajos registrado entre noviembre de 2013 y junio de 2015?**

La pregunta se desglosa en los ocho elementos definidos en el protocolo de investigación ([`Protocolo V5.pdf`](Protocolo%20V5.pdf)):

| # | Elemento | Definición en este estudio |
|---|---|---|
| 1 | **Pregunta clave** | ¿En qué medida…? Influencia de la exclusión de variables circulares en el desempeño predictivo. |
| 2 | **Variable *x*** (independiente) | Exclusión de variables circulares: modelo base (con todas las variables) frente a modelo corregido (sin las variables clasificadas como circulares). |
| 3 | **Enlace** | *Influye en* (magnitud del efecto de *x* sobre *y*). |
| 4 | **Variable *y*** (dependiente) | Desempeño predictivo del ingreso a UCI, medido con el área bajo la curva y el recall. |
| 5 | **Muestra / población** | 1,050 casos del log; 110 con ingreso a UCI (≈10 %). |
| 6 | **Ámbito de datos** | Log de eventos clínicos de un sistema ERP hospitalario, de acceso público y desidentificado. |
| 7 | **Ámbito geográfico** | Un hospital de Países Bajos. |
| 8 | **Tiempo** | Noviembre de 2013 a junio de 2015. |

---

## 4. Objetivo general

**Analizar cómo la exclusión de variables circulares modifica el desempeño predictivo de un modelo de ingreso a UCI en un log de eventos de sepsis.**

*Nota:* los objetivos son la versión vigente y podrán redefinirse al concluir la revisión del estado del arte.

---

## 5. Objetivos específicos

| Código | Objetivo específico | Verbo | Medida | Límite |
|---|---|---|---|---|
| **OE1** | Examinar la posición temporal de cada variable respecto al ingreso a UCI dentro de cada traza, para clasificarla como circular o no circular. | Examinar | Clasificación de variables (definicional, temporal o proxy) | No evalúa el desempeño predictivo |
| **OE2** | Cuantificar la diferencia de área bajo la curva y de recall entre el modelo base y el modelo corregido, con validación cruzada anidada e intervalos de confianza. | Cuantificar | Área bajo la curva, recall e intervalos de confianza por *bootstrap* | Máximo 10 variables por modelo; 110 casos positivos |
| **OE3** | Contrastar la precisión y el recall del procedimiento de detección frente a variables con fuga inyectada de intensidad conocida. | Contrastar | Precisión y recall del detector | Fugas inyectadas, no fugas reales |

**Articulación de los objetivos.** OE1 construye la variable independiente *x*, es decir, define qué variables se excluyen; sin una clasificación explícita, la exclusión no estaría definida. OE2 mide el efecto de *x* sobre la variable dependiente *y* y responde directamente a la pregunta de investigación. OE3 comprueba la validez de *x*: si el procedimiento de OE1 no identificara correctamente las fugas, el efecto medido en OE2 no sería interpretable. El objetivo general integra los tres.

---

## 6. Justificación

La investigación se justifica porque la fuga de información es un problema documentado y extendido en la ciencia basada en aprendizaje automático (Kapoor y Narayanan, 2023; Sasse et al., 2025), cuyas consecuencias son particularmente delicadas en el ámbito clínico, donde las métricas de desempeño orientan decisiones sobre pacientes. Al mismo tiempo, los logs de eventos ofrecen una propiedad que los conjuntos tabulares no tienen —el orden temporal explícito de las actividades— y que permite abordar la detección de variables circulares de manera sistemática. La justificación se desarrolla conforme a cuatro criterios: relevancia social (sección 7), conveniencia (sección 8), valor teórico (sección 9) e implicaciones prácticas (sección 10).

---

## 7. Relevancia social

La sepsis es una causa relevante de ingreso a las unidades de cuidados intensivos, y los modelos que anticipan dicho ingreso pueden apoyar las decisiones de triaje desde el servicio de urgencias (Mannhardt y Blinde, 2017; Adjerid et al., 2023). Un modelo cuya precisión está inflada por circularidad puede orientar de manera errónea esas decisiones, al aparentar una capacidad de anticipación que no tendría en la práctica. Medir el efecto real de la circularidad contribuye, por lo tanto, a que los modelos que eventualmente se utilicen en el triaje se evalúen con métricas que reflejen la información realmente disponible en el momento de decidir.

*Pendiente:* ubicar el pasaje y la página exacta de Mannhardt y Blinde (2017) que sustenta este argumento, e incorporar una fuente epidemiológica sobre sepsis e ingreso a UCI.

---

## 8. Conveniencia

El estudio es conveniente y factible por las siguientes razones:

- utiliza un log público ya disponible (Mannhardt, 2016), con un desenlace bien definido (`Admission IC`), por lo que no requiere acuerdos institucionales ni acceso a datos personales;
- se apoya en herramientas abiertas: scikit-learn, XGBoost (Chen y Guestrin, 2016) y PM4Py (Berti et al., 2019);
- su alcance —un log, un hospital y un desenlace— es ejecutable en el plazo de un programa de posgrado; y
- el orden de las actividades en el log ofrece una vía sistemática para detectar la fuga, un problema reconocido como común en el aprendizaje automático (Kapoor y Narayanan, 2023).

---

## 9. Valor teórico

El estudio vincula dos líneas de investigación que rara vez se cruzan: la literatura sobre fuga de información en aprendizaje automático (Kaufman et al., 2011; Kapoor y Narayanan, 2023; Sasse et al., 2025) y la de minería de procesos en salud (Rojas et al., 2016; Mannhardt y Blinde, 2017). Su contribución teórica es un **criterio operativo para clasificar variables según su posición en la traza** respecto al desenlace, que distingue la circularidad definicional, temporal y por *proxy*, y que se valida tanto en un log real como en uno con fugas inyectadas de intensidad conocida.

---

## 10. Implicaciones prácticas

- Si la corrección reduce el desempeño de forma relevante, los modelos reportados con este tipo de log podrían estar sobreestimados, lo que obligaría a revisar las métricas publicadas.
- El procedimiento es reutilizable en otros logs de eventos con desenlaces de ingreso o de alta.
- La validación con fugas inyectadas ofrece una forma de estimar la precisión y el recall del detector antes de aplicarlo a datos nuevos.
- Los resultados no son generalizables a otros hospitales sin una validación externa.

---

## 11. Hipótesis de investigación e hipótesis nula

Sea $\mathrm{AUC}_{\text{base}}$ el área bajo la curva del modelo base y $\mathrm{AUC}_{\text{corr}}$ la del modelo corregido, ambos estimados con el mismo algoritmo, las mismas particiones y la misma validación cruzada anidada. Se define la diferencia

$$
\Delta = \mathrm{AUC}_{\text{base}} - \mathrm{AUC}_{\text{corr}} .
$$

- **Hipótesis de investigación (H1).** El área bajo la curva del modelo corregido es menor que la del modelo base ($\Delta > 0$). La dirección se fundamenta en la evidencia de que la fuga infla el desempeño reportado (Kapoor y Narayanan, 2023; Rosenblatt et al., 2024).
- **Hipótesis nula (H0).** No existe diferencia en el área bajo la curva entre el modelo base y el modelo corregido más allá de la variación esperada por el muestreo ($\Delta = 0$).

**Criterio de contraste.** La diferencia $\Delta$ se estimará por algoritmo (regresión logística, Random Forest y XGBoost) con validación cruzada anidada repetida por semilla, y se acompañará de un intervalo de confianza por *bootstrap*. H0 se rechazará a favor de H1 cuando el intervalo de confianza de $\Delta$ se ubique por completo por encima de cero. El recall, evaluado en un umbral de decisión fijado antes de los experimentos, se reportará como métrica complementaria con el mismo procedimiento.

*Pendiente de decisión:* la variante del área bajo la curva —precisión-recall (AUC-PR), recomendable por la baja proporción de casos positivos (Davis y Goadrich, 2006), o ROC (AUC-ROC)— y el nivel de confianza del intervalo.

---

## 12. Marco teórico

El marco teórico se organiza en torno a los conceptos que sustentan cada objetivo específico.

**Fuga de información y circularidad.** La fuga de información ocurre cuando un modelo utiliza, durante el entrenamiento o la evaluación, información que no estaría disponible en el momento de la predicción, lo que produce estimaciones de desempeño optimistas (Kaufman et al., 2011; Kapoor y Narayanan, 2023). El análisis circular, o *double dipping*, describe el caso en que los mismos datos se usan para seleccionar variables y para estimar el desempeño (Kriegeskorte et al., 2009). En esta investigación, la circularidad se define por escenarios —definicional, temporal y por *proxy*— y su efecto se mide como la diferencia de desempeño entre el modelo base y el corregido (OE1 y OE2).

**Minería de procesos, log de eventos y traza.** Un log de eventos es un registro en el que cada evento corresponde a una actividad ejecutada en un caso, con su marca de tiempo y sus atributos; la secuencia ordenada de eventos de un caso constituye su traza (van der Aalst, 2016). Esta representación permite ubicar el momento de registro de cada variable respecto al ingreso a UCI, que es el fundamento del criterio temporal de OE1. El descubrimiento de modelos de proceso y el cálculo de *fitness* no forman parte de los objetivos vigentes; la minería de procesos se emplea únicamente para representar y ordenar las trazas.

**Validación de modelos.** Cuando la selección de hiperparámetros o de variables no está anidada dentro del procedimiento de evaluación, la estimación del desempeño presenta un sesgo optimista (Cawley y Talbot, 2010). Por ello, la comparación entre el modelo base y el corregido se realiza con validación cruzada anidada. En problemas con baja proporción de casos positivos, como el presente (≈10 %), el espacio precisión-recall resulta más informativo que el ROC (Davis y Goadrich, 2006).

**Algoritmos de clasificación.** Se comparan tres algoritmos con la misma validación: la regresión logística (Hosmer et al., 2013), como modelo lineal de referencia; Random Forest (Breiman, 2001), como conjunto de árboles; y XGBoost (Chen y Guestrin, 2016), como método de *boosting* de alto desempeño en datos tabulares. Cada modelo se limita a un máximo de 10 variables, con una selección documentada antes del entrenamiento.

**Detección automática de fuga y calidad de datos.** La detección de fugas se ha abordado mediante medidas cuantitativas (Hannun et al., 2021) y herramientas de análisis de código (Yang et al., 2022; Alomar et al., 2025). Para evaluar el detector propuesto, se adopta por analogía la lógica de la inyección controlada de fallos (Natella et al., 2016): se introduce una variable copia del desenlace con ruido controlado en tres niveles de intensidad y se mide la precisión y el recall con que el procedimiento la identifica (OE3). La calidad de los datos de origen condiciona el desempeño de los modelos tabulares (Mohammed et al., 2025) y se considera en la preparación del log.

---

## 13. Temas del marco teórico

La tabla relaciona cada tema con su aporte, los objetivos que sustenta y los referentes de la matriz del estado del arte (el símbolo # corresponde al número del referente en [`Estado_del_Arte_v3.xlsx`](Estado_del_Arte_v3.xlsx)).

| Tema | Aporte a la investigación | Objetivo(s) | Referentes (#) |
|---|---|---|---|
| **13.1 Fuga de información: escenarios, medición y efecto** | Definir la circularidad (definicional, temporal y *proxy*) y explicar cómo infla las métricas. | OE1, OE2, OE3 | #16, #18, #22, #23, #24, #28, #42 |
| **13.2 Validación de modelos y *pipelines*** (incluye validación anidada) | Establecer el orden correcto de validación y la comparación entre el modelo base y el corregido. | OE2 | #17, #19, #21, #29, #38 |
| **13.3 Minería de procesos: representación y orden de trazas en salud y sepsis** | Justificar el uso de trazas para ubicar cada variable respecto al ingreso a UCI. | OE1 | #1, #2, #8, #9, #11, #13, #15, #31, #32, #33, #34, #35, #37, #43, #44, #45, #46 |
| **13.4 Detección automática de fuga** | Sustentar el procedimiento de detección y su comparación con herramientas existentes. | OE3 | #25, #26, #41 |
| **13.5 Calidad de datos y limpieza** | Sustentar la preparación del log y el efecto de la calidad de los datos. | Marco general (apoya OE1 y OE2) | #20, #27 |
| **13.6 Algoritmos de clasificación** | Describir la regresión logística, Random Forest y XGBoost. | OE2 | #21, #30, #39, #40 |
| **13.7 Contexto clínico: sepsis e ingreso a UCI** | Justificar la relevancia social del desenlace. | Relevancia social | #12 |

**Relación entre el marco teórico, los objetivos y el estado del arte.**

| Objetivo | Temas que lo sustentan | Pendiente de fuente |
|---|---|---|
| General | 13.1, 13.2, 13.3 | Ninguno adicional: el objetivo general integra los tres específicos. |
| OE1 | 13.1 (circularidad temporal y definicional), 13.3 (orden de actividades en la traza) | Definición operativa de "circular" y umbral del criterio *proxy*. |
| OE2 | 13.1 (efecto de la fuga sobre las métricas), 13.2 (validación), 13.6 (algoritmos) | Incorporar a la matriz las referencias metodológicas de Random Forest (Breiman, 2001) y de regresión logística (Hosmer et al., 2013). |
| OE3 | 13.1 (medición de la fuga), 13.4 (detección automática) | Definición formal de la precisión y el recall del detector; el método de inyección tiene referencia por analogía (#41). |

---

## Referencias

Formato APA 7. Las referencias marcadas con † no figuran aún en la matriz del estado del arte y se incorporaron como referencias metodológicas.

Adjerid, I., Ayvaci, M. U. S., & Özer, Ö. (2023). Value of algorithm-enabled process innovation: The case of sepsis. *Manufacturing & Service Operations Management*. https://doi.org/10.1287/msom.2023.1226

Alomar, E. A., Demario, C., Shagawat, R., & Kreiser, B. (2025). *LeakageDetector: An open source data leakage analysis tool in machine learning pipelines* (arXiv:2503.14723). arXiv. https://arxiv.org/abs/2503.14723

Aversano, L., Iammarino, M., & Madau, A. (2025). Process mining applications in healthcare: A systematic literature review. *PeerJ Computer Science*. https://peerj.com/articles/cs-2613/

Berti, A., van Zelst, S. J., & van der Aalst, W. M. P. (2019). Process mining for Python (PM4Py): Bridging the gap between process- and data science. En *Proceedings of the ICPM Demo Track 2019* (CEUR Workshop Proceedings, Vol. 2374, pp. 13–16). CEUR-WS.org. https://ceur-ws.org/Vol-2374/paper4.pdf

† Breiman, L. (2001). Random forests. *Machine Learning, 45*(1), 5–32. https://doi.org/10.1023/A:1010933404324

Cawley, G. C., & Talbot, N. L. C. (2010). On over-fitting in model selection and subsequent selection bias in performance evaluation. *Journal of Machine Learning Research, 11*, 2079–2107. https://jmlr.org/papers/v11/cawley10a.html

Chen, T., & Guestrin, C. (2016). XGBoost: A scalable tree boosting system. En *Proceedings of the 22nd ACM SIGKDD International Conference on Knowledge Discovery and Data Mining* (pp. 785–794). ACM. https://doi.org/10.1145/2939672.2939785

Davis, J., & Goadrich, M. (2006). The relationship between precision-recall and ROC curves. En *Proceedings of the 23rd International Conference on Machine Learning* (pp. 233–240). ACM. https://doi.org/10.1145/1143844.1143874

Hannun, A., Guo, C., & van der Maaten, L. (2021). Measuring data leakage in machine-learning models with Fisher information. En *Proceedings of the Thirty-Seventh Conference on Uncertainty in Artificial Intelligence* (Proceedings of Machine Learning Research, Vol. 161, pp. 760–770). PMLR.

† Hosmer, D. W., Jr., Lemeshow, S., & Sturdivant, R. X. (2013). *Applied logistic regression* (3.ª ed.). Wiley. https://doi.org/10.1002/9781118548387

Kapoor, S., & Narayanan, A. (2023). Leakage and the reproducibility crisis in machine-learning-based science. *Patterns, 4*(9), 100804. https://doi.org/10.1016/j.patter.2023.100804

Kaufman, S., Rosset, S., & Perlich, C. (2011). Leakage in data mining: Formulation, detection, and avoidance. En *Proceedings of the 17th ACM SIGKDD International Conference on Knowledge Discovery and Data Mining* (pp. 556–563). ACM. https://doi.org/10.1145/2020408.2020496

Kriegeskorte, N., Simmons, W. K., Bellgowan, P. S. F., & Baker, C. I. (2009). Circular analysis in systems neuroscience: The dangers of double dipping. *Nature Neuroscience, 12*(5), 535–540. https://doi.org/10.1038/nn.2303

Mannhardt, F. (2016). *Sepsis cases – Event log* [Conjunto de datos]. 4TU.ResearchData. https://doi.org/10.4121/uuid:915d2bfb-7e84-49ad-a286-dc35f063a460

Mannhardt, F., & Blinde, D. (2017). Analyzing the trajectories of patients with sepsis using process mining. En *RADAR+EMISA 2017* (CEUR Workshop Proceedings, Vol. 1859, pp. 72–80). CEUR-WS.org. https://ceur-ws.org/Vol-1859/bpmds-08-paper.pdf

Mohammed, S., et al. (2025). The effects of data quality on machine learning performance on tabular data. *Information Systems, 132*, 102549. https://doi.org/10.1016/j.is.2025.102549

Natella, R., Cotroneo, D., & Madeira, H. (2016). Assessing dependability with software fault injection: A survey. *ACM Computing Surveys, 48*(3), Artículo 44. https://doi.org/10.1145/2841425

Pereira, G. B., Santos, E. A. P., & Maceno, M. M. C. (2020). Process mining project methodology in healthcare: A case study in a tertiary hospital. [Datos de publicación por confirmar: la matriz registra *Health Information Science and Systems*, 9, art. 28].

Quintano Neira, R. A., Hompes, B. F. A., de Vries, J. G.-J., Mazza, B. F., Simões de Almeida, S. L., Stretton, E., Buijs, J. C. A. M., & Hamacher, S. (2020). Analysis and optimization of a sepsis clinical pathway using process mining. Springer Nature [capítulo de libro; datos de publicación por confirmar].

Rebuge, Á., & Ferreira, D. R. (2012). Business process analysis in healthcare environments: A methodology based on process mining. *Information Systems* [volumen y páginas por confirmar].

Rojas, E., Munoz-Gama, J., Sepúlveda, M., & Capurro, D. (2016). Process mining in healthcare: A literature review. *Journal of Biomedical Informatics, 61*, 224–236. https://doi.org/10.1016/j.jbi.2016.04.007

Rosenblatt, M., Tejavibulya, L., Jiang, R., Noble, S., & Scheinost, D. (2024). Data leakage inflates prediction performance in connectome-based machine learning models. *Nature Communications, 15*, 1829. https://doi.org/10.1038/s41467-024-46150-w

Sasse, L., Nicolaisen-Sobesky, E., Dukart, J., Eickhoff, S. B., Götz, M., Hamdan, S., Komeyer, V., Kulkarni, A., Lahnakoski, J. M., Love, B. C., Raimondo, F., & Patil, K. R. (2025). Overview of leakage scenarios in supervised machine learning. *Journal of Big Data, 12*, 135. https://doi.org/10.1186/s40537-025-01193-8

Silva Júnior, E. R., Santos, U. L., & Figueredo, M. B. (2023). Process mining in sepsis treatment management: A step-by-step approach to discovery. *Journal of Bioengineering, Technologies and Health*. https://doi.org/10.34178/jbth.v6iSuppl2.354

van der Aalst, W. M. P. (2016). *Process mining: Data science in action* (2.ª ed.). Springer. https://doi.org/10.1007/978-3-662-49851-4

Yang, C., Brower-Sinning, R. A., Lewis, G., & Kästner, C. (2022). Data leakage in notebooks: Static detection and better processes. En *Proceedings of the 37th IEEE/ACM International Conference on Automated Software Engineering (ASE '22)*. ACM. https://doi.org/10.1145/3551349.3556918

---

<div align="center">

*© 2026 Jessica Melani Romero Lora.*

</div>
