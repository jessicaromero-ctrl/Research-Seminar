<div align="center">

# Detección y exclusión de variables circulares en modelos de ingreso a UCI

### Un procedimiento sobre logs de eventos clínicos con machine learning y minería de procesos

**Universidad Politécnica Metropolitana del Estado de Hidalgo**

**Maestría en Inteligencia Artificial**

**Autora:** Jessica Melani Romero Lora
**Director de tesis:** Dr. Marcos Yamir Gómez

**Versión:** 0.5 · **Estado:** en construcción · **Fecha:** octubre de 2026

![Estado](https://img.shields.io/badge/estado-en%20construcci%C3%B3n-orange) ![Licencia](https://img.shields.io/badge/derechos-reservados-red) ![Datos](https://img.shields.io/badge/datos-p%C3%BAblicos%20desidentificados-blue)

</div>

---

## ⚠️ Aviso de estado y derechos

- **Prototipo en construcción.** Los objetivos, los resultados y las referencias pueden cambiar. Ninguna cifra de este repositorio es final.
- **Todos los derechos reservados.** © 2026 Jessica Melani Romero Lora. El contenido se comparte con fines de revisión académica. No se autoriza su reproducción, distribución ni uso comercial sin permiso escrito de la autora.
- **Sin licencia de software.** El repositorio no incluye una licencia de código abierto. Si la autora decide publicar el código bajo una licencia, debe agregarse un archivo `LICENSE` antes de compartirlo.

---

## 🔒 Protección de datos

1. **Datos personales.** El proyecto no procesa datos personales identificables. El log utilizado es público y viene desidentificado por su fuente.
2. **Sin datos institucionales ni de terceros.** No se usan datos de ninguna empresa, institución de salud ni empleador. Ningún dato interno de organizaciones se incluye en este repositorio.
3. **Sin reidentificación.** Está prohibido intentar reidentificar a pacientes, casos o personas a partir de los datos.
4. **Uso restringido al propósito académico.** Los datos se usan solo para los fines descritos en este README.
5. **No redistribución de la base de datos.** Este repositorio no contiene una copia del log. Las instrucciones de descarga apuntan a la fuente original. Antes de redistribuir cualquier archivo derivado, verificar los términos de uso de la fuente.
6. **Revisión antes de publicar.** Antes de cada publicación, revisar que no haya credenciales, rutas locales, matrículas, correos personales ni datos sensibles en el código o en los archivos.

---

## 📌 Resumen

El proyecto estudia cómo la exclusión de **variables circulares** modifica el desempeño predictivo de un modelo de **ingreso a unidad de cuidados intensivos (UCI)** en un log de eventos de sepsis. Una variable es circular cuando contiene información del propio desenlace, ya sea porque lo define, porque se registra después de él o porque actúa como proxy fuerte. Esa información no está disponible en el momento de la predicción, y su presencia infla el desempeño reportado.

El procedimiento combina tres componentes:
- **Minería de procesos** para ubicar cada variable en la traza respecto al ingreso a UCI.
- **Machine learning** para comparar un modelo base con un modelo corregido.
- **Validación con datos con fuga inyectada** para medir la precisión del procedimiento de detección.

---

## 🎯 Pregunta de investigación

¿En qué medida la exclusión de variables circulares influye en el desempeño predictivo del ingreso a UCI, en el log Sepsis Cases de un hospital de Países Bajos registrado entre noviembre de 2013 y junio de 2015?

---

## 🧭 Objetivos

*Versión vigente. Se redefinirán después de la revisión del estado del arte.*

**Objetivo general.** Analizar cómo la exclusión de variables circulares modifica el desempeño predictivo de un modelo de ingreso a UCI en un log de eventos de sepsis.

| Código | Objetivo específico | Verbo |
|---|---|---|
| OE1 | Examinar la posición temporal de cada variable respecto al ingreso a UCI dentro de cada traza, para clasificarla como circular o no circular. | Examinar |
| OE2 | Cuantificar la diferencia de área bajo la curva y de recall entre el modelo base y el modelo corregido, con validación cruzada anidada e intervalos de confianza. | Cuantificar |
| OE3 | Contrastar la precisión y el recall del procedimiento de detección frente a variables con fuga inyectada de intensidad conocida. | Contrastar |

**Relación entre objetivos.** OE1 define la variable que el estudio manipula (qué se excluye). OE2 mide el efecto de esa exclusión sobre el desempeño. OE3 comprueba que la clasificación de OE1 sea correcta.

---

## 🧪 Diseño

| Elemento | Definición |
|---|---|
| Tipo de estudio | Experimental computacional, con un factor (exclusión de variables circulares) y dos niveles (modelo base y modelo corregido) |
| Datos | Log Sepsis Cases (4TU.ResearchData): 1,050 casos y 15,214 eventos, 16 actividades |
| Desenlace | Ingreso a UCI (`Admission IC`): 110 casos (cerca del 10%) |
| Punto de predicción | Solo atributos del primer evento (registro en urgencias) |
| Atributos | La documentación oficial reporta 39. El archivo analizado contiene **27 atributos propios**. Se trabaja con los 27 del archivo y la diferencia se declara como limitación |
| Clasificación de variables | Definicional, temporal o proxy (criterios en la sección de metodología del protocolo) |
| Restricción de tamaño | Máximo 10 variables por modelo, con selección documentada antes de entrenar |
| Validación | Validación cruzada anidada, repetida por semilla; intervalos de confianza por bootstrap |
| Prueba del detector | Variable copia del desenlace con ruido controlado en tres niveles |

---

## 🤖 Algoritmos y métricas

**Algoritmos (comparativa con la misma validación):**
- Regresión logística
- Random Forest
- XGBoost

**Métricas principales:**
- **Área bajo la curva.** La variante está por confirmar: área bajo la curva precisión-recall (AUC-PR), por la baja proporción de casos positivos, o área bajo la curva ROC (AUC-ROC).
- **Recall**, en el umbral de decisión que se fije antes de los experimentos.

---

## 📐 Justificación

**Relevancia social.** La sepsis es una causa relevante de ingreso a UCI, y los modelos que anticipan ese ingreso pueden apoyar el triaje. Un modelo con precisión inflada por circularidad puede orientar mal esas decisiones. Fuente de referencia: Mannhardt y Blinde (2017), sobre el log de sepsis del proyecto. *[Ubicar pasaje y página exacta antes de citar.]*

**Conveniencia.** El procedimiento usa un log público, herramientas abiertas (scikit-learn, XGBoost, PM4Py) y un desenlace bien definido. Es ejecutable en el plazo de un posgrado y no requiere acuerdos institucionales.

**Valor teórico.** Relaciona la literatura sobre fuga de datos en aprendizaje automático con la de minería de procesos en salud. La contribución es un criterio operativo para clasificar variables según su posición en la traza, validado en un log real y en uno con fugas inyectadas.

**Implicaciones prácticas.** Si la corrección reduce el desempeño de forma relevante, los modelos reportados con este tipo de log pueden estar sobreestimados. El procedimiento puede reutilizarse en otros logs con desenlaces de ingreso o alta. Los resultados no se generalizan a otros hospitales sin validación externa.

---

## 🧾 Hipótesis

- **H1.** El área bajo la curva del modelo corregido es menor que la del modelo base (Kapoor y Narayanan, 2023).
- **H0.** No hay diferencia en el área bajo la curva entre el modelo base y el modelo corregido, más allá de la variación esperada por el muestreo.

---

## 📚 Estado del arte

El estado del arte reúne **46 referencias** organizadas por tema:

| Bloque | Número de referencias |
|---|---|
| Minería de procesos en salud, sepsis y descubrimiento | 26 |
| Fuga de datos, validación, algoritmos y métricas | 20 |

La tabla completa, con año, revista, país, objetivo relacionado, aporte por referencia y estado de verificación, está en [`estado_del_arte/Estado_del_Arte_v3.xlsx`](estado_del_arte/Estado_del_Arte_v3.xlsx).

**Estado de verificación.** Una referencia está verificada solo si se confirmó contra la fuente original. Actualmente, 28 de 46 están marcadas como verificadas y 18 quedan pendientes.

**Pendientes del estado del arte:**
- Definiciones operativas de circularidad adicionales a Kriegeskorte et al. (2009).
- Referencia metodológica de Random Forest (Breiman, 2001) y de regresión logística.
- Definición formal de precisión y recall del detector.
- Pasaje y página exacta de la relevancia social en Mannhardt y Blinde (2017).

---

## 🗂️ Estructura del repositorio

```
.
├── README.md                          Este documento
├── DECISIONES.md                      Registro de decisiones del proyecto
├── docs/
│   └── Protocolo_breve_v5_6.docx      Protocolo breve (estructura del Dr. Zamudio)
├── estado_del_arte/
│   └── Estado_del_Arte_v3.xlsx        Tabla de referencias, objetivos y marco teórico
├── datos/
│   └── README_datos.md                Instrucciones de descarga (sin copia del log)
├── resultados/                        Figuras y tablas (pendiente)
└── src/                               Código (pendiente)
```

**Excluido del repositorio público:** `archivo_previo/`, que contiene versiones anteriores del proyecto. Sus contenidos no forman parte de la propuesta vigente.

---

## 📥 Datos

**Fuente:** Mannhardt, F. (2016). *Sepsis Cases – Event Log*. 4TU.ResearchData. DOI: [10.4121/uuid:915d2bfb-7e84-49ad-a286-dc35f063a460](https://doi.org/10.4121/uuid:915d2bfb-7e84-49ad-a286-dc35f063a460)

**Cómo obtenerlo:** descargar desde la fuente original y colocar el archivo en `datos/` (carpeta excluida del control de versiones).

**Características verificadas:**
- Hospital de Países Bajos (Eindhoven University of Technology, publicador 4TU.Centre for Research Data)
- Periodo de cobertura: noviembre de 2013 a junio de 2015
- 1,050 casos, 16 actividades, 15,214 eventos
- Marcas de tiempo aleatorizadas por caso; el tiempo entre eventos dentro de cada traza no se altera

---

## ⚙️ Reproducción

*Pendiente. El código se publicará cuando esté validado el procedimiento de OE1 y OE2.*

Dependencias previstas: Python 3, PM4Py, scikit-learn, XGBoost, pandas, numpy. Las versiones se fijarán en `requirements.txt` antes de la primera ejecución.

---

## 🗓️ Historial de versiones

| Versión | Descripción |
|---|---|
| v0.5 | Protocolo breve con estructura del Dr. Zamudio; estado del arte de 46 referencias; decisiones de alcance (ML y minería de procesos sobre un log público). |
| v4 | Protocolo reducido; alcance concentrado en un solo log; cadena de Markov eliminada. |
| v3 | Protocolo con 7 objetivos y estado del arte de 17 referentes (archivado). |

---

## 📬 Contacto

Jessica Melani Romero Lora · *(correo institucional por confirmar)*

---

<div align="center">

*© 2026 Jessica Melani Romero Lora. Todos los derechos reservados.*

</div>
