# Skill: Exakte Pfade (Methode 2)

Du bekommst die exakten Fundstellen. Du musst NICHTS suchen und KEINE anderen
Dateien lesen. Wende direkt `str_replace` mit dem angegebenen alten Wert an.

Platzhalter in der Tabelle:
- `<NEU_GROSS>` = neuer Variantenname in GROSSBUCHSTABEN (z. B. ENTRY)
- `<Neu>`       = neuer Variantenname, erster Buchstabe gross, Rest klein (z. B. Entry)
- `<neu>`       = neuer Variantenname komplett klein (z. B. entry)

Zu aendernde Stellen (jeweils der komplette Feldwert in der stage.json):

| Nr | Datei                                     | Feld               | Alter Wert                 | Neuer Wert              |
|----|-------------------------------------------|--------------------|----------------------------|-------------------------|
| 1  | stages/stage01_netzteil/stage.json        | variantenkennung   | "VARIANTX"                 | "<NEU_GROSS>"           |
| 2  | stages/stage02_kabel/stage.json           | variant_id         | "TL-Variantx-01"           | "TL-<Neu>-01"           |
| 3  | stages/stage03_schalter/stage.json        | modellname         | "tischlampe_variantx"      | "tischlampe_<neu>"      |
| 4  | stages/stage04_fassung/stage.json         | produktlinie       | "variantxevo"              | "<neu>evo"              |
| 5  | stages/stage05_leuchtmittel/stage.json    | hardware_variante  | "HW-VariantxEVO"           | "HW-<Neu>EVO"           |
| 6  | stages/stage06_schirm/stage.json          | sku_variante       | "SKU-VARIANTX-2024"        | "SKU-<NEU_GROSS>-2024"  |
| 7  | stages/stage07_standfuss/stage.json       | baureihe           | "Variantx"                 | "<Neu>"                 |
| 8  | stages/stage08_gelenkarm/stage.json       | cad_projekt        | "cad_variantx_arm"         | "cad_<neu>_arm"         |
| 9  | stages/stage09_dimmer/stage.json          | kalibrierprofil    | "dim_variantxevo.cal"      | "dim_<neu>evo.cal"      |
| 10 | stages/stage10_verpackung/stage.json      | etikett_name       | "Tischlampe VariantxEVO"   | "Tischlampe <Neu>EVO"   |

Vorgehen:
1. Fuehre fuer jede Zeile der Tabelle genau ein `str_replace` aus
   (old_str = alter Wert inkl. Anfuehrungszeichen, new_str = neuer Wert inkl. Anfuehrungszeichen).
2. Aendere sonst nichts. Benutze keine Hilfsskripte.
