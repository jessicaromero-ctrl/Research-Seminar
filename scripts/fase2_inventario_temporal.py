import logging
from pathlib import Path

import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
log = logging.getLogger("fase2_inventario_temporal")

RUTA = Path("datos/sepsis/procesado/sepsis_events_corregido.csv")
SALIDA = Path("semana_2026-11-02/resultados/fase2_inventario_temporal.csv")
COL_CASO = "case:concept:name"
COL_ACT = "concept:name"
COL_TIEMPO = "time:timestamp"
COL_IC = "Admission IC"
META = [COL_CASO, COL_ACT, COL_TIEMPO, "lifecycle:transition", "org:group"]


def main() -> None:
    df = pd.read_csv(RUTA, low_memory=False)
    df[COL_TIEMPO] = pd.to_datetime(df[COL_TIEMPO], utc=True)
    df = df.sort_values([COL_CASO, COL_TIEMPO], kind="stable").reset_index(drop=True)
    df["pos"] = df.groupby(COL_CASO).cumcount()

    # t0: primer evento de cada caso (D9)
    t0 = df.loc[df["pos"] == 0].set_index(COL_CASO)[COL_TIEMPO]
    df["t0"] = df[COL_CASO].map(t0)

    # t_ic: momento del ingreso a UCI; NaN en casos negativos
    t_ic = df.loc[df[COL_ACT] == COL_IC].groupby(COL_CASO)[COL_TIEMPO].min()
    df["t_ic"] = df[COL_CASO].map(t_ic)

    n_casos = df[COL_CASO].nunique()
    n_pos = df["t_ic"].notna().groupby(df[COL_CASO]).any().sum()
    log.info("Casos: %d | Positivos (Admission IC): %d", n_casos, n_pos)

    empates = df[(df["pos"] > 0) & (df[COL_TIEMPO] == df["t0"])]
    log.info("Eventos posteriores al primero con la misma marca de t0: %d", len(empates))

    atributos = [c for c in df.columns if c not in META + ["pos", "t0", "t_ic"]]
    log.info("Atributos analizados: %d (esperado: 27)", len(atributos))

    filas = []
    for attr in atributos:
        con_valor = df[attr].notna()
        valores = int(con_valor.sum())
        if valores == 0:
            filas.append({"atributo": attr, "valores": 0})
            continue
        antes_t0 = int((con_valor & (df[COL_TIEMPO] <= df["t0"])).sum())
        despues_ic = int((con_valor & df["t_ic"].notna() & (df[COL_TIEMPO] > df["t_ic"])).sum())
        moda = df.loc[con_valor, COL_ACT].mode()
        filas.append({
            "atributo": attr,
            "valores": valores,
            "valores_en_t0_o_antes": antes_t0,
            "valores_despues_de_IC": despues_ic,
            "actividad_principal": moda.iloc[0] if not moda.empty else "-",
        })

    tabla = pd.DataFrame(filas)
    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    tabla.to_csv(SALIDA, index=False)
    print(tabla.to_string(index=False))
    log.info("Tabla guardada en %s", SALIDA)


if __name__ == "__main__":
    main()

