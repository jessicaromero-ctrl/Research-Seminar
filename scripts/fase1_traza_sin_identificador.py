import logging
from pathlib import Path

import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
log = logging.getLogger("fase1_traza_sin_identificador")

RUTA = Path("datos/sepsis/original/sepsis_full_events.csv")
COL_CASO = "case:concept:name"
COL_ACTIVIDAD = "concept:name"
COL_TIEMPO = "time:timestamp"


def main() -> None:
    df = pd.read_csv(RUTA, low_memory=False)
    sin_id = df[df[COL_CASO].isna()]
    log.info("Eventos sin identificador: %d", len(sin_id))
    log.info("Rango de filas en el CSV: %d a %d", sin_id.index.min(), sin_id.index.max())
    log.info("Contiene Admission IC: %s", bool((sin_id[COL_ACTIVIDAD] == "Admission IC").any()))
    print("\n== Secuencia de la traza sin identificador ==")
    print(sin_id[[COL_ACTIVIDAD, COL_TIEMPO]].to_string())
    print("\n== Frecuencia de actividades ==")
    print(sin_id[COL_ACTIVIDAD].value_counts().to_string())


if __name__ == "__main__":
    main()