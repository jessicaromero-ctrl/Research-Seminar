import logging
from pathlib import Path

import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
log = logging.getLogger("fase2_cardinalidad_diagnose")

RUTA = Path("datos/sepsis/procesado/sepsis_events_corregido.csv")
SALIDA = Path("semana_2026-11-02/resultados/fase2_cardinalidad_diagnose.csv")
COL_CASO = "case:concept:name"
COL_TIEMPO = "time:timestamp"
ACT_T0 = "ER Registration"
UMBRAL = 10


def main() -> None:
    df = pd.read_csv(RUTA, low_memory=False)
    df[COL_TIEMPO] = pd.to_datetime(df[COL_TIEMPO], utc=True)
    t0 = df.loc[df["concept:name"] == ACT_T0].groupby(COL_CASO)[COL_TIEMPO].min()
    df["t0"] = df[COL_CASO].map(t0)

    # D11a: valores de Diagnose con marca <= t0
    disp = df.loc[df["Diagnose"].notna() & (df[COL_TIEMPO] <= df["t0"])]
    conteo = disp.groupby("Diagnose")[COL_CASO].nunique().sort_values(ascending=False)

    log.info("Casos con Diagnose disponible en t0: %d", disp[COL_CASO].nunique())
    log.info("Códigos distintos: %d", len(conteo))
    log.info("Códigos con >= %d casos: %d", UMBRAL, int((conteo >= UMBRAL).sum()))
    log.info("Casos cubiertos por esos códigos: %d", int(conteo[conteo >= UMBRAL].sum()))
    log.info("Códigos que aparecen en un solo caso: %d", int((conteo == 1).sum()))

    print(conteo.head(15).to_string())
    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    conteo.rename("casos").to_csv(SALIDA)


if __name__ == "__main__":
    main()
