import logging
from pathlib import Path

import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
log = logging.getLogger("fase2_dx_vs_ic")

RUTA = Path("datos/sepsis/procesado/sepsis_events_corregido.csv")
SALIDA = Path("semana_2026-11-02/resultados/fase2_dx_vs_ic.csv")
COL_CASO = "case:concept:name"
COL_ACT = "concept:name"
COL_TIEMPO = "time:timestamp"
ACT_T0 = "ER Registration"
ACT_IC = "Admission IC"


def main() -> None:
    df = pd.read_csv(RUTA, low_memory=False)
    df[COL_TIEMPO] = pd.to_datetime(df[COL_TIEMPO], utc=True)

    t0 = df.loc[df[COL_ACT] == ACT_T0].groupby(COL_CASO)[COL_TIEMPO].min()
    t_ic = df.loc[df[COL_ACT] == ACT_IC].groupby(COL_CASO)[COL_TIEMPO].min()
    df["t0"] = df[COL_CASO].map(t0)
    df["t_ic"] = df[COL_CASO].map(t_ic)

    # Clase: solo para describir, no para seleccionar variables
    positivos = list(t_ic.index)
    df["clase"] = df[COL_CASO].isin(positivos).map({True: "positivo", False: "negativo"})

    dx = df.loc[df["Diagnose"].notna()].copy()
    dx["momento"] = "antes_o_en_t0"
    dx.loc[dx[COL_TIEMPO] > dx["t0"], "momento"] = "posterior_t0"
    dx.loc[(dx[COL_TIEMPO] > dx["t0"]) & (dx[COL_TIEMPO] > dx["t_ic"]), "momento"] = "posterior_IC"

    print("\n== Registros de Diagnose por clase y momento ==")
    print(dx.groupby(["clase", "momento"]).size().unstack(fill_value=0).to_string())

    por_caso = dx.groupby(COL_CASO)["Diagnose"].nunique()
    log.info("Casos con Diagnose: %d", len(por_caso))
    log.info("Casos con más de un código distinto dentro de la traza: %d", int((por_caso > 1).sum()))
    log.info("Casos con Diagnose posterior a Admission IC: %d",
             dx.loc[dx["momento"] == "posterior_IC", COL_CASO].nunique())

    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    dx[[COL_CASO, COL_ACT, COL_TIEMPO, "Diagnose", "clase", "momento"]].to_csv(SALIDA, index=False)
    log.info("Detalle guardado en %s", SALIDA)


if __name__ == "__main__":
    main()
