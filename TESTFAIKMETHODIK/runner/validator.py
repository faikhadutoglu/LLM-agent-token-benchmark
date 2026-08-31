"""Prueft ein Ergebnisprojekt gegen die Referenz (Vorlage + Soll-Werte)."""
import json
from pathlib import Path

from .naming import formen


def pruefe_variante(projekt: Path, vorlage: Path, variante: str):
    """Rueckgabe: (bestanden, bericht_text, felder_ok, felder_gesamt, dateien_ok, dateien_gesamt)"""
    f = formen(variante)
    manifest = json.loads(
        (vorlage / "tools" / "variant_manifest.json").read_text(encoding="utf-8"))
    zeilen = []
    felder_ok = 0

    # 1) Die 10 Zieldateien: Inhalt muss der Vorlage entsprechen,
    #    nur das Zielfeld traegt den neuen (korrekt geschriebenen) Wert.
    for e in manifest:
        soll_wert = e["muster"].replace("{X}", f[e["form"]])
        soll = json.loads((vorlage / e["datei"]).read_text(encoding="utf-8"))
        soll[e["feld"]] = soll_wert
        pfad = projekt / e["datei"]
        try:
            ist = json.loads(pfad.read_text(encoding="utf-8"))
        except Exception as ex:
            zeilen.append(f"FEHLER  {e['datei']}: nicht lesbar oder kein JSON ({ex})")
            continue
        if ist == soll:
            felder_ok += 1
            zeilen.append(f"OK      {e['datei']}  ({e['feld']} = {soll_wert!r})")
        else:
            ist_wert = ist.get(e["feld"], "<Feld fehlt>")
            zeilen.append(f"FEHLER  {e['datei']}: erwartet {e['feld']} = {soll_wert!r}, "
                          f"gefunden {ist_wert!r} (oder andere Abweichung in der Datei)")

    # 2) Alle uebrigen Dateien unter stages/ muessen unveraendert sein.
    ziel_dateien = {e["datei"] for e in manifest}
    sonstige = [p for p in sorted((vorlage / "stages").rglob("*"))
                if p.is_file() and p.relative_to(vorlage).as_posix() not in ziel_dateien]
    dateien_ok = 0
    for p in sonstige:
        rel = p.relative_to(vorlage).as_posix()
        q = projekt / rel
        if q.exists() and q.read_text(encoding="utf-8") == p.read_text(encoding="utf-8"):
            dateien_ok += 1
        else:
            zeilen.append(f"FEHLER  {rel}: wurde veraendert oder fehlt")

    bestanden = felder_ok == len(manifest) and dateien_ok == len(sonstige)
    kopf = [
        f"Pruefbericht  Variante: {variante}",
        f"Zielfelder korrekt:            {felder_ok}/{len(manifest)}",
        f"Uebrige Dateien unveraendert:  {dateien_ok}/{len(sonstige)}",
        f"Gesamtergebnis:                {'BESTANDEN' if bestanden else 'NICHT BESTANDEN'}",
        "-" * 70,
    ]
    bericht = "\n".join(kopf + zeilen) + "\n"
    return bestanden, bericht, felder_ok, len(manifest), dateien_ok, len(sonstige)
