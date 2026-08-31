"""Agent-Schleife: ruft die Claude-API mit Werkzeugen auf, bis die Aufgabe fertig ist."""
import json
import os
import subprocess
import sys
from pathlib import Path

MAX_TOOL_RESULT = 20000

BASIS_WERKZEUGE = [
    {
        "name": "list_dir",
        "description": "Listet Dateien ([F]) und Ordner ([D]) in einem Verzeichnis des Projekts auf.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Relativer Pfad, '.' fuer den Projektstamm"},
                "recursive": {"type": "boolean", "description": "Optional: rekursiv auflisten"},
            },
            "required": ["path"],
        },
    },
    {
        "name": "read_file",
        "description": "Liest eine Textdatei im Projekt und gibt den Inhalt zurueck.",
        "input_schema": {
            "type": "object",
            "properties": {"path": {"type": "string", "description": "Relativer Pfad zur Datei"}},
            "required": ["path"],
        },
    },
    {
        "name": "str_replace",
        "description": "Ersetzt einen exakt einmal vorkommenden Text in einer Datei.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string"},
                "old_str": {"type": "string", "description": "Muss exakt einmal in der Datei vorkommen"},
                "new_str": {"type": "string"},
            },
            "required": ["path", "old_str", "new_str"],
        },
    },
    {
        "name": "write_file",
        "description": "Erstellt oder ueberschreibt eine Datei mit komplettem Inhalt.",
        "input_schema": {
            "type": "object",
            "properties": {"path": {"type": "string"}, "content": {"type": "string"}},
            "required": ["path", "content"],
        },
    },
]

APPLY_WERKZEUG = {
    "name": "run_apply_tool",
    "description": "Fuehrt 'python tools/apply_variant.py' im Projektstamm aus und gibt die Ausgabe zurueck.",
    "input_schema": {"type": "object", "properties": {}},
}


def lade_api_key(basis: Path) -> str:
    key = os.environ.get("ANTHROPIC_API_KEY", "").strip() 
    if not key:
        datei = basis / "api_key.txt"
        if datei.exists():
            key = datei.read_text(encoding="utf-8").strip()
    if not key:
        raise RuntimeError(
            "Kein API-Key gefunden. Umgebungsvariable ANTHROPIC_API_KEY setzen "
            "oder Datei api_key.txt (nur der Key) in TESTFAIKMETHODIK anlegen.")
    return key


def _sicherer_pfad(root: Path, rel: str) -> Path:
    p = (root / rel).resolve()
    root = root.resolve()
    if p != root and root not in p.parents:
        raise ValueError(f"Pfad liegt ausserhalb des Projekts: {rel}")
    return p


def _werkzeug_ausfuehren(projekt: Path, name: str, args: dict) -> str:
    try:
        if name == "list_dir":
            p = _sicherer_pfad(projekt, args.get("path", "."))
            if not p.is_dir():
                return f"FEHLER: kein Verzeichnis: {args.get('path')}"
            eintraege = sorted(p.rglob("*")) if args.get("recursive") else sorted(p.iterdir())
            zeilen = [f"{'[D]' if q.is_dir() else '[F]'} {q.relative_to(projekt).as_posix()}"
                      for q in eintraege]
            return "\n".join(zeilen) or "(leer)"
        if name == "read_file":
            return _sicherer_pfad(projekt, args["path"]).read_text(encoding="utf-8")
        if name == "str_replace":
            p = _sicherer_pfad(projekt, args["path"])
            text = p.read_text(encoding="utf-8")
            n = text.count(args["old_str"])
            if n == 0:
                return "FEHLER: old_str nicht gefunden."
            if n > 1:
                return f"FEHLER: old_str kommt {n}-mal vor, muss eindeutig sein."
            p.write_text(text.replace(args["old_str"], args["new_str"]), encoding="utf-8")
            return "OK: ersetzt."
        if name == "write_file":
            p = _sicherer_pfad(projekt, args["path"])
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(args["content"], encoding="utf-8")
            return "OK: geschrieben."
        if name == "run_apply_tool":
            r = subprocess.run(
                [sys.executable, str(projekt / "tools" / "apply_variant.py")],
                cwd=str(projekt), capture_output=True, text=True, timeout=60)
            return f"exit={r.returncode}\n{r.stdout}\n{r.stderr}".strip()
        return f"FEHLER: unbekanntes Werkzeug: {name}"
    except Exception as e:  # Fehler zurueck an das Modell geben
        return f"FEHLER: {e}"


def agent_ausfuehren(projekt: Path, system_prompt: str, user_prompt: str,
                     mit_apply_tool: bool, modell: str, max_tokens: int,
                     max_turns: int, api_key: str, log_datei: Path):
    """Fuehrt einen kompletten Agenten-Lauf aus.

    Rueckgabe: (verbrauch_dict, anzahl_api_aufrufe)
    """
    import anthropic
    client = anthropic.Anthropic(api_key=api_key)
    werkzeuge = list(BASIS_WERKZEUGE) + ([APPLY_WERKZEUG] if mit_apply_tool else [])
    messages = [{"role": "user", "content": user_prompt}]
    verbrauch = {"input_tokens": 0, "output_tokens": 0,
                 "cache_creation_input_tokens": 0, "cache_read_input_tokens": 0}
    aufrufe = 0

    with open(log_datei, "w", encoding="utf-8") as lf:
        lf.write("SYSTEM-PROMPT:\n" + system_prompt + "\n\n")
        lf.write("USER-PROMPT:\n" + user_prompt + "\n" + "=" * 70 + "\n")
        for runde in range(1, max_turns + 1):
            antwort = client.messages.create(
                model=modell, max_tokens=max_tokens, system=system_prompt,
                tools=werkzeuge, messages=messages)
            aufrufe += 1
            u = antwort.usage
            verbrauch["input_tokens"] += u.input_tokens
            verbrauch["output_tokens"] += u.output_tokens
            verbrauch["cache_creation_input_tokens"] += getattr(u, "cache_creation_input_tokens", 0) or 0
            verbrauch["cache_read_input_tokens"] += getattr(u, "cache_read_input_tokens", 0) or 0
            lf.write(f"\n--- Runde {runde} (stop={antwort.stop_reason}, "
                     f"in={u.input_tokens}, out={u.output_tokens}) ---\n")

            messages.append({"role": "assistant", "content": antwort.content})
            ergebnisse = []
            for block in antwort.content:
                if block.type == "text":
                    lf.write("[TEXT] " + block.text + "\n")
                elif block.type == "tool_use":
                    lf.write(f"[TOOL] {block.name} "
                             f"{json.dumps(block.input, ensure_ascii=False)[:600]}\n")
                    out = _werkzeug_ausfuehren(projekt, block.name, block.input)
                    if len(out) > MAX_TOOL_RESULT:
                        out = out[:MAX_TOOL_RESULT] + "\n...(gekuerzt)"
                    lf.write("[ERGEBNIS] " + out[:800].replace("\n", " | ") + "\n")
                    ergebnisse.append({"type": "tool_result",
                                       "tool_use_id": block.id, "content": out})
            if antwort.stop_reason != "tool_use" or not ergebnisse:
                break
            messages.append({"role": "user", "content": ergebnisse})
        else:
            lf.write("\nABBRUCH: max_turns erreicht.\n")
        lf.write(f"\nVERBRAUCH: {json.dumps(verbrauch)}  API-Aufrufe: {aufrufe}\n")
    return verbrauch, aufrufe
