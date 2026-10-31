import logging
from pathlib import Path

import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
log = logging.getLogger("fase2_disponibilidad_t0")

RUTA = Path("datos/sepsis/procesado/sepsis_events_corregido.csv")
SALIDA = Path("semana_2026-11-02/resultados/fase2_disponibilidad_t0.csv")
COL_CASO = "case:concept:name"
COL_ACT = "concept:name"
COL_TIEMPO = "time:timestamp"
META = [COL_CASO, COL_ACT, COL_TIEMPO, "lifecycle:transition", "org:group"]
ACT_T0 = "ER Registration"
ACT_IC = "Admission IC"


def main() -> None:
    df = pd.read_csv(RUTA, low_memory=False)
    df[COL_TIEMPO] = pd.to_datetime(df[COL_TIEMPO], utc=True)
    df = df.sort_values([COL_CASO, COL_TIEMPO], kind="stable").reset_index(drop=True)

    # D9 revisada: t0 = marca de ER Registration
    t0 = df.loc[df[COL_ACT] == ACT_T0].groupby(COL_CASO)[COL_TIEMPO].min()
    df["t0"] = df[COL_CASO].map(t0)

    # Clase: positivo si el caso tiene Admission IC (D11a no usa esta clase; solo se reporta)
    casos = pd.Index(df[COL_CASO].unique(), name=COL_CASO)
    positivos = set(df.loc[df[COL_ACT] == ACT_IC, COL_CASO])
    es_pos = pd.Series(casos.isin(list(positivos)), index=casos)
    n_pos, n_neg = int(es_pos.sum()), int((~es_pos).sum())
    log.info("Positivos: %d | Negativos: %d", n_pos, n_neg)

    atributos = [c for c in df.columns if c not in META + ["t0"]]
    filas = []
    for attr in atributos:
        con = df[attr].notna()
        # D11a: disponible en t0 = existe un valor con marca <= t0 en el caso
        ids = df.loc[con & (df[COL_TIEMPO] <= df["t0"]), COL_CASO].unique()
        disp = pd.Series(casos.isin(ids), index=casos)
        pct_pos = 100 * (disp & es_pos).sum() / n_pos
        pct_neg = 100 * (disp & ~es_pos).sum() / n_neg
        filas.append({
            "atributo": attr,
            "disponible_t0_casos": int(disp.sum()),
            "pct_disp_positivos": round(pct_pos, 2),
            "pct_disp_negativos": round(pct_neg, 2),
            "diferencia_pp": round(pct_pos - pct_neg, 2),
            "valores_distintos": int(df[attr].nunique(dropna=True)),
        })

    tabla = pd.DataFrame(filas).sort_values("disponible_t0_casos", ascending=False)
    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    tabla.to_csv(SALIDA, index=False)
    print(tabla.to_string(index=False))

    print("\n== Valores observados en atributos con 5 o menos categorías ==")
    for attr in atributos:
        if df[attr].nunique(dropna=True) <= 5:
            print(f"{attr}: {df[attr].value_counts(dropna=False).to_dict()}")

    log.info("Tabla guardada en %s", SALIDA)


if __name__ == "__main__":
    main()
