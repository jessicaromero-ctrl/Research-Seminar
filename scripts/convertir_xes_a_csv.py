"""Convierte el log oficial Sepsis Cases (XES) a un CSV plano: una fila por evento.

Uso (desde cualquier carpeta):
    python scripts/convertir_xes_a_csv.py

Lee   datos/sepsis/original/Sepsis Cases - Event Log.xes.gz
Escribe datos/sepsis/original/sepsis_full_events.csv
Imprime además un resumen del log (casos, eventos, actividades, atributos,
casos con Admission IC, altas por tipo y eventos de laboratorio con valor).
"""
import gzip, pathlib
REPO = pathlib.Path(__file__).resolve().parent.parent
DATOS = REPO / "datos" / "sepsis" / "original"
import xml.etree.ElementTree as ET, csv, collections
with gzip.open(DATOS / "Sepsis Cases - Event Log.xes.gz", "rb") as fx:
    root=ET.parse(fx).getroot()
def tag(e): return e.tag.split('}')[-1]
TYPES={'string','date','int','float','boolean','id'}
# global declarations
for g in root:
    if tag(g)=='global': print("GLOBAL",g.get('scope'),[a.get('key') for a in g])
traces=[t for t in root if tag(t)=='trace']
tkeys=collections.Counter(); ekeys=collections.Counter(); acts=collections.Counter()
rows=[]; nev=0; ic=0; rel=collections.Counter(); lab=collections.Counter()
ekeytypes=collections.defaultdict(set)
for t in traces:
    ta={a.get('key'):a.get('value') for a in t if tag(a) in TYPES}
    for k in ta: tkeys[k]+=1
    evs=[e for e in t if tag(e)=='event']
    names=set()
    for e in evs:
        ea={}
        for a in e:
            if tag(a) in TYPES: ea[a.get('key')]=a.get('value'); ekeytypes[a.get('key')].add(tag(a))
        for k in ea: ekeys[k]+=1
        n=ea.get('concept:name'); acts[n]+=1; names.add(n); nev+=1
        if n in('Leucocytes','CRP','LacticAcid'): lab[(n,'has_value')]+= n in ea
        r={'case:'+k:v for k,v in ta.items()}; r.update(ea); rows.append(r)
    if 'Admission IC' in names: ic+=1
    for n in names:
        if n.startswith('Release'): rel[n]+=1
print("traces",len(traces),"events",nev,"activities",len(acts))
for a,c in acts.most_common(): print(" ",a,c)
print("TRACE keys",len(tkeys),dict(tkeys))
print("EVENT keys",len(ekeys)); [print(" ",k,c,ekeytypes[k]) for k,c in ekeys.most_common()]
print("union distinct keys",len(set(tkeys)|set(ekeys)))
print("cases with Admission IC",ic); print("cases per Release",dict(rel))
print("lab events with value attr",dict(lab))
cols=sorted({k for r in rows for k in r})
lead=[c for c in ['case:concept:name','concept:name','time:timestamp','lifecycle:transition','org:group'] if c in cols]
cols=lead+[c for c in cols if c not in lead]
with open(DATOS / 'sepsis_full_events.csv','w',newline='',encoding='utf-8') as fh:
    w=csv.DictWriter(fh,fieldnames=cols); w.writeheader(); w.writerows(rows)
print("csv cols",len(cols),cols)
