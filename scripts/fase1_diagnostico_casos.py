import logging
import xml.etree.ElementTree as ET
from pathlib import Path

import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
log = logging.getLogger("fase1_diagnostico")

RUTA_XES = Path("datos/sepsis/original/Sepsis Cases - Event Log.xes")
RUTA_CSV = Path("datos/sepsis/original/sepsis_full_events.csv")
COL_CASO = "case:concept:name"


def casos_desde_xes(ruta: Path) -> pd.DataFrame:
    """Lee cada <trace> del XES oficial y cuenta sus <event>."""
    registros = []
    for _, elem in ET.iterparse(ruta, events=("end",)):
        if elem.tag.endswith("trace"):
            nombre, n_eventos = None, 0
            for hijo in elem:
                if hijo.tag.endswith("string") and hijo.get("key") == "concept:name":
                    nombre = hijo.get("value")
                elif hijo.tag.endswith("event"):
                    n_eventos += 1
            registros.append((nombre, n_eventos))
            elem.clear()
    df = pd.DataFrame(registros, columns=["caso", "eventos_xes"])
    log.info("Trazas en el XES: %d", len(df))
    return df


def casos_desde_csv(ruta: Path) -> pd.DataFrame:
    df = pd.read_csv(ruta, usecols=[COL_CASO])
    log.info("Filas sin identificador de caso en el CSV: %d", df[COL_CASO].isna().sum())
    conteo = df.groupby(COL_CASO).size().rename("eventos_csv").reset_index()
    return conteo.rename(columns={COL_CASO: "caso"})


if __name__ == "__main__":
    xes = casos_desde_xes(RUTA_XES)
    csv = casos_desde_csv(RUTA_CSV)
    print("\n== Trazas del XES sin eventos ==")
    print(xes[xes["eventos_xes"] == 0].to_string(index=False) or "Ninguna")
    print("\n== Trazas del XES que no aparecen en el CSV ==")
    faltan = xes.merge(csv, on="caso", how="left", indicator=True)
    print(faltan[faltan["_merge"] == "left_only"].to_string(index=False) or "Ninguna")
    print("\n== Casos con eventos distinto en XES y CSV ==")
    comun = faltan[faltan["_merge"] == "both"]
    print(comun[comun["eventos_xes"] != comun["eventos_csv"]].to_string(index=False) or "Ninguno")