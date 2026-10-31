import logging
from pathlib import Path

import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
log = logging.getLogger("fase2_diagnostico_t0")

RUTA = Path("datos/sepsis/procesado/sepsis_events_corregido.csv")
SALIDA = Path("semana_2026-11-02/resultados/fase2_casos_sin_er_inicial.csv")
COL_CASO = "case:concept:name"
COL_ACT = "concept:name"
COL_TIEMPO = "time:timestamp"
ACT_T0 = "ER Registration"


def main() -> None:
    df = pd.read_csv(RUTA, low_memory=False)
    df[COL_TIEMPO] = pd.to_datetime(df[COL_TIEMPO], utc=True)
    df = df.sort_values([COL_CASO, COL_TIEMPO], kind="stable").reset_index(drop=True)
    df["pos"] = df.groupby(COL_CASO).cumcount()

    primer = df.loc[df["pos"] == 0, [COL_CASO, COL_ACT, COL_TIEMPO]].rename(
        columns={COL_ACT: "primera_actividad", COL_TIEMPO: "t_primer_evento"})
    er = df.loc[df[COL_ACT] == ACT_T0]
    er_info = (er.groupby(COL_CASO)
                 .agg(n_er=(COL_ACT, "size"), pos_er=("pos", "min"), t_er=(COL_TIEMPO, "min"))
                 .reset_index())
    tabla = primer.merge(er_info, on=COL_CASO, how="left")
    tabla["minutos_hasta_er"] = (tabla["t_er"] - tabla["t_primer_evento"]).dt.total_seconds() / 60

    no_inicia = tabla[tabla["primera_actividad"] != ACT_T0]
    log.info("Casos que no inician en %s: %d de %d", ACT_T0, len(no_inicia), len(tabla))
    log.info("Casos sin ningún %s: %d", ACT_T0, int(tabla["n_er"].isna().sum()))
    log.info("Casos con más de un %s: %d", ACT_T0, int((tabla["n_er"] > 1).sum()))

    print("\n== Primera actividad de los casos que no inician en ER Registration ==")
    print(no_inicia["primera_actividad"].value_counts().to_string())
    print("\n== Posición de ER Registration en esos casos (0 = primer evento) ==")
    print(no_inicia["pos_er"].value_counts(dropna=False).to_string())
    print("\n== Minutos desde el primer evento hasta ER Registration ==")
    print(no_inicia["minutos_hasta_er"].describe().round(1).to_string())

    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    no_inicia.to_csv(SALIDA, index=False)
    log.info("Detalle guardado en %s", SALIDA)


if __name__ == "__main__":
    main()

