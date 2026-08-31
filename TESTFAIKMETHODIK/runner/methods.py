"""Definition der 4 Methoden und Aufbau der Prompts."""
from pathlib import Path

from .naming import formen

METHODEN = {
    1: {"schluessel": "methode1_selbst_suchen",
        "titel": "Methode 1: Selbst suchen",
        "agent": "agents/agent1_sucher.md",
        "skill": "skills/method1_selbst_suchen/SKILL.md",
        "apply_tool": False},
    2: {"schluessel": "methode2_exakte_pfade",
        "titel": "Methode 2: Exakte Pfade",
        "agent": "agents/agent2_pfadfolger.md",
        "skill": "skills/method2_exakte_pfade/SKILL.md",
        "apply_tool": False},
    3: {"schluessel": "methode3_semantische_karte",
        "titel": "Methode 3: Semantische Karte",
        "agent": "agents/agent3_kartenleser.md",
        "skill": "skills/method3_semantische_karte/SKILL.md",
        "apply_tool": False},
    4: {"schluessel": "methode4_variant_json_tool",
        "titel": "Methode 4: variant.json + Tool",
        "agent": "agents/agent4_toolnutzer.md",
        "skill": "skills/method4_variant_json_tool/SKILL.md",
        "apply_tool": True},
}

ALLGEMEINE_REGELN = (
    "\n\nAllgemeine Regeln:\n"
    "- Arbeite nur mit den bereitgestellten Werkzeugen im Projektverzeichnis.\n"
    "- Relative Pfade beziehen sich auf den Projektstamm.\n"
    "- Wenn die Aufgabe erledigt ist, antworte ohne Werkzeugaufruf nur mit FERTIG."
)


def system_prompt(basis: Path, nr: int) -> str:
    m = METHODEN[nr]
    agent = (basis / m["agent"]).read_text(encoding="utf-8")
    skill = (basis / m["skill"]).read_text(encoding="utf-8")
    return agent + "\n\n" + skill + ALLGEMEINE_REGELN


def user_prompt(nr: int, variante: str) -> str:
    if nr == 4:
        return (f'Leite im vorliegenden Tischlampen-Projekt die neue Variante "{variante}" '
                f'aus der Platzhalter-Variante "Variantx" ab. Gehe exakt nach deinem Skill vor.')
    f = formen(variante)
    return (f'Leite im vorliegenden Tischlampen-Projekt die neue Variante "{variante}" '
            f'aus der Platzhalter-Variante "Variantx" ab.\n\n'
            'Die Platzhalterkennung kommt im Projekt in 5 Schreibweisen vor '
            'und muss exakt so ersetzt werden:\n'
            f'- VARIANTX    -> {f["VARIANTX"]}\n'
            f'- Variantx    -> {f["Variantx"]}\n'
            f'- variantx    -> {f["variantx"]}\n'
            f'- variantxevo -> {f["variantxevo"]}\n'
            f'- VariantxEVO -> {f["VariantxEVO"]}\n\n'
            'Gross-/Kleinschreibung muss exakt stimmen. Aendere sonst nichts.')
