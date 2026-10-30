import logging
from pathlib import Path

import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
log = logging.getLogger("fase1_verificacion")

RUTA = Path("datos/sepsis/procesado/sepsis_events_corregido.csv")
COL_CASO = "case:concept:name"       # ajustar según el encabezado real
COL_ACTIVIDAD = "concept:name"       # ajustar según el encabezado real
COL_TIEMPO = "time:timestamp"        # ajustar según el encabezado real
ACTIVIDAD_OBJETIVO = "Admission IC"
ESPERADO = {"casos": 1050, "eventos": 15214, "actividades": 16}


def cargar(ruta: Path) -> pd.DataFrame:
    if not ruta.exists():
        raise FileNotFoundError(f"No se encontró el archivo: {ruta}")
    df = pd.read_csv(ruta, low_memory=False)
    faltantes = [c for c in (COL_CASO, COL_ACTIVIDAD, COL_TIEMPO) if c not in df.columns]
    if faltantes:
        raise KeyError(f"Columnas no encontradas: {faltantes}. Columnas disponibles: {list(df.columns)}")
    df[COL_TIEMPO] = pd.to_datetime(df[COL_TIEMPO], utc=True, errors="coerce")
    log.info("Eventos cargados: %d | Columnas: %d", len(df), len(df.columns))
    return df


def verificar_estructura(df: pd.DataFrame) -> dict:
    resumen = {
        "casos": df[COL_CASO].nunique(),
        "eventos": len(df),
        "actividades": df[COL_ACTIVIDAD].nunique(),
        "timestamps_invalidos": int(df[COL_TIEMPO].isna().sum()),
    }
    for clave, esperado in ESPERADO.items():
        if resumen[clave] != esperado:
            log.warning("%s: obtenido=%s, esperado=%s", clave, resumen[clave], esperado)
        else:
            log.info("%s: OK (%s)", clave, resumen[clave])
    return resumen


def desbalance_clase(df: pd.DataFrame) -> pd.Series:
    total = df[COL_CASO].nunique()
    positivos = df.loc[df[COL_ACTIVIDAD] == ACTIVIDAD_OBJETIVO, COL_CASO].nunique()
    log.info("Casos con %s: %d de %d (%.1f %%)", ACTIVIDAD_OBJETIVO, positivos, total, 100 * positivos / total)
    return pd.Series({"positivos": positivos, "negativos": total - positivos,
                    "proporcion_positiva": round(positivos / total, 4)})


def primer_evento(df: pd.DataFrame) -> pd.DataFrame:
    """Una fila por caso: el primer evento en orden de tiempo, con sus valores originales."""
    return (
        df.sort_values([COL_CASO, COL_TIEMPO], kind="stable")
        .drop_duplicates(subset=COL_CASO, keep="first")
    )


def faltantes_por_atributo(df: pd.DataFrame) -> pd.DataFrame:
    excluir = [COL_CASO, COL_ACTIVIDAD, COL_TIEMPO, "lifecycle:transition", "org:group"]
    atributos = df.drop(columns=excluir, errors="ignore")
    pe = primer_evento(df).drop(columns=excluir, errors="ignore")
    log.info("Filas en primer evento: %d (debe coincidir con casos)", len(pe))
    tabla = pd.DataFrame({
        "faltante_en_eventos_pct": 100 * atributos.isna().mean(),
        "faltante_en_primer_evento_pct": 100 * pe.isna().mean(),
    })
    return tabla.sort_values("faltante_en_primer_evento_pct", ascending=False).round(2)