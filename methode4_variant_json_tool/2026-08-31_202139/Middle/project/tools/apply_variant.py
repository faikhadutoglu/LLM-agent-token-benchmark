# apply_variant.py
# Liest variant.json im Projektstamm und schreibt die Variantenkennung
# in der jeweils richtigen Schreibweise in alle Stage-Dateien (siehe variant_manifest.json).
# Aufruf aus dem Projektstamm:  python tools/apply_variant.py
import json
from pathlib import Path

BASIS = Path(__file__).resolve().parent.parent


def formen(name: str) -> dict:
    """Leitet aus dem Variantennamen alle 5 Schreibweisen ab."""
    cap = name[:1].upper() + name[1:].lower()
    low = name.lower()
    return {
        "VARIANTX": name.upper(),
        "Variantx": cap,
        "variantx": low,
        "variantxevo": low + "evo",
        "VariantxEVO": cap + "EVO",
    }


def main() -> None:
    variant = json.loads((BASIS / "variant.json").read_text(encoding="utf-8"))["variant_name"]
    f = formen(variant)
    manifest = json.loads(
        (Path(__file__).resolve().parent / "variant_manifest.json").read_text(encoding="utf-8"))
    for eintrag in manifest:
        pfad = BASIS / eintrag["datei"]
        daten = json.loads(pfad.read_text(encoding="utf-8"))
        neuer_wert = eintrag["muster"].replace("{X}", f[eintrag["form"]])
        daten[eintrag["feld"]] = neuer_wert
        pfad.write_text(json.dumps(daten, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"OK  {eintrag['datei']}  ->  {eintrag['feld']} = {neuer_wert}")
    print(f"Fertig: {len(manifest)} Dateien aktualisiert (Variante: {variant})")


if __name__ == "__main__":
    main()
