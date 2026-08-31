# Skill: variant.json + Tool (Methode 4)

Alle Varianten-Aenderungen sind in EINER Datei zentralisiert: `variant.json`
im Projektstamm. Das Hilfsskript `tools/apply_variant.py` schreibt die Kennung
automatisch in der richtigen Schreibweise in alle betroffenen Stage-Dateien.

Vorgehen:
1. Lies `variant.json` mit `read_file`.
2. Setze mit `str_replace` das Feld `variant_name` auf den neuen Namen
   (Schreibweise: erster Buchstabe gross, Rest klein, z. B. "Entry").
3. Fuehre `run_apply_tool` aus.
4. Aendere KEINE anderen Dateien. Danach bist du fertig.
