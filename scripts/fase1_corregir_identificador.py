import logging
from pathlib import Path

import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
log = logging.getLogger("fase1_corregir_identificador")

ENTRADA = Path("datos/sepsis/original/sepsis_full_events.csv")
SALIDA = Path("datos/sepsis/procesado/sepsis_events_corregido.csv")
COL_CASO = "case:concept:name"
COL_ACTIVIDAD = "concept:name"
ID_FALTANTE = "caso_sin_identificador"


def main() -> None:
    df = pd.read_csv(ENTRADA, low_memory=False)
    n_faltantes = int(df[COL_CASO].isna().sum())
    log.info("Filas sin identificador de caso: %d", n_faltantes)

    # Comprobación de seguridad (decisión D5): la traza sin nombre no debe contener Admission IC
    con_ic = df.loc[df[COL_CASO].isna() & (df[COL_ACTIVIDAD] == "Admission IC")]
    assert con_ic.empty, "Hay Admission IC en la traza sin identificador. Revisar antes de continuar."

    df[COL_CASO] = df[COL_CASO].fillna(ID_FALTANTE)
    log.info("Casos únicos tras la corrección: %d", df[COL_CASO].nunique())

    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(SALIDA, index=False)
    log.info("Archivo guardado en %s", SALIDA)


if __name__ == "__main__":
    main()
