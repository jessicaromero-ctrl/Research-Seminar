import logging
from pathlib import Path

import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
log = logging.getLogger("fase2_ausencia_diagnose")

RUTA = Path("datos/sepsis/procesado/sepsis_events_corregido.csv")
SALIDA = Path("semana_2026-11-02/resultados/fase2_ausencia_diagnose.csv")
COL_CASO = "case:concept:name"
COL_ACT = "concept:name"
COL_TIEMPO = "time:timestamp"
ACT_T0 = "ER Registration"


def main() -> None:
    df = pd.read_csv(RUTA, low_memory=False)
    df[COL_TIEMPO] = pd.to_datetime(df[COL_TIEMPO], utc=True)
    df = df.sort_values([COL_CASO, COL_TIEMPO], kind="stable").reset_index(drop=True)
    t0 = df.loc[df[COL_ACT] == ACT_T0].groupby(COL_CASO)[COL_TIEMPO].min()
    df["t0"] = df[COL_CASO].map(t0)

    casos = pd.Index(df[COL_CASO].unique())
    con_dx = df.loc[df["Diagnose"].notna()].copy()
    dx_en_t0 = set(con_dx.loc[con_dx[COL_TIEMPO] <= con_dx["t0"], COL_CASO])
    alguna_dx = set(con_dx[COL_CASO])
    sin_dx_t0 = [c for c in casos if c not in dx_en_t0]
    nunca = [c for c in sin_dx_t0 if c not in alguna_dx]
    despues = [c for c in sin_dx_t0 if c in alguna_dx]
    log.info("Casos sin Diagnose en t0: %d", len(sin_dx_t0))
    log.info("  Mecanismo A (nunca registrado): %d", len(nunca))
    log.info("  Mecanismo B (registrado después de t0): %d", len(despues))

    desfase = (con_dx[COL_TIEMPO] - con_dx["t0"]).dt.total_seconds() / 60
    log.info("Registros de Diagnose antes de t0: %d | en t0: %d | después: %d",
             int((desfase < 0).sum()), int((desfase == 0).sum()), int((desfase > 0).sum()))

    # Mecanismo C: actividad que comparte marca exacta con cada registro de Diagnose
    otros = df.loc[df["Diagnose"].isna(), [COL_CASO, COL_ACT, COL_TIEMPO]]
    cruce = con_dx[[COL_CASO, COL_TIEMPO]].merge(otros, on=[COL_CASO, COL_TIEMPO], how="left")
    print("\n== Actividad que comparte marca con Diagnose (mecanismo C) ==")
    print(cruce[COL_ACT].fillna("(sin otra actividad con esa marca)").value_counts().head(12).to_string())

    # Resumen por caso
    primera = df.groupby(COL_CASO)[COL_ACT].first()
    resumen = pd.DataFrame({
        "caso": casos,
        "primera_actividad": primera.reindex(casos).values,
        "sin_dx_en_t0": [c in set(sin_dx_t0) for c in casos],
        "dx_en_algun_momento": [c in alguna_dx for c in casos],
    })
    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    resumen.to_csv(SALIDA, index=False)
    log.info("Resumen guardado en %s", SALIDA)


if __name__ == "__main__":
    main()

