# Semantische Karte - Tischlampen-Projekt

Diese Karte beschreibt, welcher Ordner und welche Datei wofuer zustaendig ist.

## Projektstamm
- `variant.json`: zentrale Varianten-Definition (nur fuer den automatisierten Tool-Workflow relevant)
- `tools/`: Hilfsskripte (`apply_variant.py` schreibt die Variante automatisch in alle Stages)
- `stages/`: die 10 Entwicklungs-/Fertigungsstufen der Tischlampe

## Wichtig fuer Varianten-Aenderungen
Die Varianten-/Produktkennung einer Stage steht IMMER in der `stage.json`
der jeweiligen Stage (der Feldname ist je Stage unterschiedlich).
Alle uebrigen Dateien (`README.md`, `config.yaml`, `bom.csv`, `pruefplan.txt`,
`notizen.txt`) enthalten KEINE Variantenkennung und muessen dafuer nicht
gelesen oder geaendert werden.

## Stages im Detail
- `stages/stage01_netzteil/`: Netzteil und Stromversorgung.
  Dateien: stage.json (Metadaten + Kennung), README.md, config.yaml, bom.csv, pruefplan.txt
- `stages/stage02_kabel/`: Zuleitung und Verkabelung.
  Dateien: stage.json (Metadaten + Kennung), config.yaml, notizen.txt
- `stages/stage03_schalter/`: Ein-/Ausschalter am Kabel.
  Dateien: stage.json (Metadaten + Kennung), README.md, config.yaml, bom.csv, pruefplan.txt
- `stages/stage04_fassung/`: Lampenfassung E27.
  Dateien: stage.json (Metadaten + Kennung), config.yaml, notizen.txt
- `stages/stage05_leuchtmittel/`: LED-Leuchtmittel.
  Dateien: stage.json (Metadaten + Kennung), README.md, config.yaml, bom.csv, pruefplan.txt
- `stages/stage06_schirm/`: Lampenschirm aus Textil.
  Dateien: stage.json (Metadaten + Kennung), config.yaml, notizen.txt
- `stages/stage07_standfuss/`: Standfuss und Gewicht.
  Dateien: stage.json (Metadaten + Kennung), README.md, config.yaml, bom.csv, pruefplan.txt
- `stages/stage08_gelenkarm/`: Verstellbarer Gelenkarm.
  Dateien: stage.json (Metadaten + Kennung), config.yaml, notizen.txt
- `stages/stage09_dimmer/`: Touch-Dimmer-Elektronik.
  Dateien: stage.json (Metadaten + Kennung), README.md, config.yaml, bom.csv, pruefplan.txt
- `stages/stage10_verpackung/`: Verpackung und Etikettierung.
  Dateien: stage.json (Metadaten + Kennung), config.yaml, notizen.txt
