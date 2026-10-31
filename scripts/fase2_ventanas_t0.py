import logging
from pathlib import Path

import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
log = logging.getLogger("fase2_ventanas_t0")

RUTA = Path("datos/sepsis/procesado/sepsis_events_corregido.csv")
SALIDA = Path("semana_2026-11-02/resultados/fase2_ventanas_t0.csv")
SALIDA_SIMULTANEOS = Path("semana_2026-11-02/resultados/fase2_eventos_simultaneos_t0.csv")
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

    # D9 revisada: t0 = marca de ER Registration; debe existir exactamente uno por caso
    er = df.loc[df[COL_ACT] == ACT_T0]
    casos = df[COL_CASO].unique()
    conteo_er = er.groupby(COL_CASO).size().reindex(casos, fill_value=0)
    log.info("Casos con 0 ER Registration: %d", int((conteo_er == 0).sum()))
    log.info("Casos con 1 ER Registration: %d", int((conteo_er == 1).sum()))
    log.info("Casos con más de 1 ER Registration: %d", int((conteo_er > 1).sum()))
    assert (conteo_er == 1).all(), "Algún caso no tiene exactamente un ER Registration. Revisar D9."

    t0 = er.groupby(COL_CASO)[COL_TIEMPO].min()
    df["t0"] = df[COL_CASO].map(t0)
    t_ic = df.loc[df[COL_ACT] == ACT_IC].groupby(COL_CASO)[COL_TIEMPO].min()
    df["t_ic"] = df[COL_CASO].map(t_ic)
    es_pos = df["t_ic"].notna()

    # Verificación: ningún Admission IC debe ocurrir antes de t0
    ic_previo = int((es_pos & (df["t_ic"] < df["t0"])).groupby(df[COL_CASO]).any().sum())
    log.info("Casos positivos con Admission IC anterior a t0: %d", ic_previo)

    # Eventos distintos de ER Registration con la misma marca exacta de t0
    simultaneos = df[(df[COL_TIEMPO] == df["t0"]) & (df[COL_ACT] != ACT_T0)]
    log.info("Eventos simultáneos a t0 (distintos de ER Registration): %d en %d casos",
             len(simultaneos), simultaneos[COL_CASO].nunique())
    SALIDA_SIMULTANEOS.parent.mkdir(parents=True, exist_ok=True)
    simultaneos[[COL_CASO, COL_ACT, COL_TIEMPO]].to_csv(SALIDA_SIMULTANEOS, index=False)

    atributos = [c for c in df.columns if c not in META + ["t0", "t_ic"]]
    log.info("Atributos analizados: %d (esperado: 27)", len(atributos))

    filas = []
    for attr in atributos:
        con = df[attr].notna()
        antes_t0 = con & (df[COL_TIEMPO] < df["t0"])
        en_t0 = con & (df[COL_TIEMPO] == df["t0"])
        ventana = con & (df[COL_TIEMPO] > df["t0"]) & (~es_pos | (df[COL_TIEMPO] <= df["t_ic"]))
        despues_ic = con & es_pos & (df[COL_TIEMPO] > df["t_ic"])
        total = int(con.sum())
        suma = int(antes_t0.sum() + en_t0.sum() + ventana.sum() + despues_ic.sum())
        # Las cuatro ventanas deben particionar todos los valores del atributo
        assert suma == total, f"Las ventanas no suman el total en {attr}"
        filas.append({
            "atributo": attr,
            "valores_total": total,
            "antes_de_t0": int(antes_t0.sum()),
            "en_t0": int(en_t0.sum()),
            "post_t0_pre_IC": int(ventana.sum()),
            "despues_de_IC": int(despues_ic.sum()),
            "casos_con_valor_en_t0": int(df.loc[en_t0, COL_CASO].nunique()),
        })

    tabla = pd.DataFrame(filas)
    SALIDA.parent.mkdir(parents=True, exist_ok=True)
    tabla.to_csv(SALIDA, index=False)
    print(tabla.to_string(index=False))
    log.info("Tabla guardada en %s", SALIDA)


if __name__ == "__main__":
    main()

