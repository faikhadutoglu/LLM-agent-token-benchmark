"""Namensableitung: aus einem Variantennamen alle 5 Schreibweisen erzeugen."""

PLATZHALTER = ["VARIANTX", "Variantx", "variantx", "variantxevo", "VariantxEVO"]


def formen(name: str) -> dict:
    cap = name[:1].upper() + name[1:].lower()
    low = name.lower()
    return {
        "VARIANTX": name.upper(),
        "Variantx": cap,
        "variantx": low,
        "variantxevo": low + "evo",
        "VariantxEVO": cap + "EVO",
    }
