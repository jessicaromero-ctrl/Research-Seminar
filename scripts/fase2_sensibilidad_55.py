import pandas as pd
from pathlib import Path

RUTA = Path("datos/sepsis/procesado/sepsis_events_corregido.csv")
SALIDA = Path("semana_2026-11-02/resultados/fase2_sensibilidad_55.csv")
C, A, T = "case:concept:name", "concept:name", "time:timestamp"
ACT_T0, ACT_IC = "ER Registration", "Admission IC"
ATRIBUTOS = ["Age", "Diagnose", "CRP", "LacticAcid", "Leucocytes"]

df = pd.read_csv(RUTA, low_memory=False)
df[T] = pd.to_datetime(df[T], utc=True)
df = df.sort_values([C, T], kind="stable").reset_index(drop=True)
t0 = df[df[A] == ACT_T0].groupby(C)[T].min()
df["t0"] = df[C].map(t0)
primera = df.groupby(C)[A].first()
grupo55 = set(primera[primera != ACT_T0].index)
positivos = set(df.loc[df[A] == ACT_IC, C])
todos = pd.Index(df[C].unique())
sin55 = todos[~todos.isin(list(grupo55))]

def tabla(casos, etiqueta):
    es_pos = pd.Series(casos.isin(list(positivos)), index=casos)
    n_pos, n_neg = int(es_pos.sum()), int((~es_pos).sum())
    filas = []
    for attr in ATRIBUTOS:
        con = df[attr].notna() & (df[T] <= df["t0"]) & df[C].isin(casos)
        disp = pd.Series(casos.isin(list(set(df.loc[con, C]))), index=casos)
        p_pos = 100 * (disp & es_pos).sum() / n_pos
        p_neg = 100 * (disp & ~es_pos).sum() / n_neg
        filas.append({
            "universo": etiqueta, "atributo": attr,
            "n_casos": len(casos), "n_pos": n_pos, "n_neg": n_neg,
            "cobertura_total_pct": round(100 * disp.mean(), 2),
            "pct_pos": round(p_pos, 2), "pct_neg": round(p_neg, 2),
            "dif_pp": round(p_pos - p_neg, 2),
        })
    return filas

resultado = pd.DataFrame(tabla(todos, "todos") + tabla(sin55, "sin_grupo_55"))
print(resultado.to_string(index=False))
SALIDA.parent.mkdir(parents=True, exist_ok=True)
resultado.to_csv(SALIDA, index=False)
print(f"\nGuardado en {SALIDA}")
