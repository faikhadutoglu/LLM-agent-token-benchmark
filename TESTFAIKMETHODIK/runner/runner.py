"""Orchestrierung: 5 Varianten-Laeufe pro Methode + Berichte + Selbsttest."""
import datetime
import json
import shutil
import subprocess
import sys
import time
from pathlib import Path

from .agent_loop import agent_ausfuehren, lade_api_key
from .methods import METHODEN, system_prompt, user_prompt
from .validator import pruefe_variante

BASIS = Path(__file__).resolve().parent.parent
VORLAGE = BASIS / "projekt_vorlage"


def lade_config() -> dict:
    return json.loads((BASIS / "config.json").read_text(encoding="utf-8"))


def _leerer_verbrauch() -> dict:
    return {"input_tokens": 0, "output_tokens": 0,
            "cache_creation_input_tokens": 0, "cache_read_input_tokens": 0}


def run_methode(nr: int, log=print) -> Path:
    """Fuehrt fuer Methode nr alle 5 Varianten-Laeufe aus und schreibt report.txt."""
    cfg = lade_config()
    api_key = lade_api_key(BASIS)
    m = METHODEN[nr]
    stempel = datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")
    lauf_dir = BASIS / "results" / m["schluessel"] / stempel
    lauf_dir.mkdir(parents=True)
    sp = system_prompt(BASIS, nr)

    log(f"== {m['titel']} ==  Modell: {cfg['model']}  Ergebnisse: {lauf_dir}")
    ergebnisse = []
    for variante in cfg["varianten"]:
        vdir = lauf_dir / variante
        projekt = vdir / "project"
        shutil.copytree(VORLAGE, projekt)
        log(f"-> Variante '{variante}': Agent startet ...")
        fehler = ""
        t0 = time.perf_counter()
        try:
            verbrauch, aufrufe = agent_ausfuehren(
                projekt, sp, user_prompt(nr, variante), m["apply_tool"],
                cfg["model"], cfg["max_tokens"], cfg["max_turns"],
                api_key, vdir / "agent_log.txt")
        except Exception as ex:
            fehler = f"{type(ex).__name__}: {ex}"
            verbrauch, aufrufe = _leerer_verbrauch(), 0
        dauer = time.perf_counter() - t0

        ok, bericht, fo, fg, do, dg = pruefe_variante(projekt, VORLAGE, variante)
        (vdir / "pruefung.txt").write_text(bericht, encoding="utf-8")
        status = "BESTANDEN" if ok and not fehler else "NICHT BESTANDEN"
        log(f"   '{variante}': {status} | {dauer:.1f} s | API-Aufrufe: {aufrufe} | "
            f"Tokens in/out: {verbrauch['input_tokens']}/{verbrauch['output_tokens']}"
            + (f" | FEHLER: {fehler}" if fehler else ""))
        ergebnisse.append({"variante": variante, "ok": ok and not fehler,
                           "felder": f"{fo}/{fg}", "dateien": f"{do}/{dg}",
                           "dauer_s": dauer, "aufrufe": aufrufe,
                           "verbrauch": verbrauch, "fehler": fehler})

    _schreibe_report(lauf_dir, m["titel"], cfg["model"], ergebnisse)
    log(f"Report: {lauf_dir / 'report.txt'}")
    return lauf_dir


def _schreibe_report(lauf_dir: Path, titel: str, modell: str, ergebnisse: list) -> None:
    z = ["=" * 78,
         "TESTFAIKMETHODIK - Bericht",
         titel,
         f"Modell: {modell}",
         f"Erstellt: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
         "=" * 78, "",
         f"{'Variante':<10} {'Ergebnis':<16} {'Felder':<8} {'Dateien':<9} "
         f"{'Zeit(s)':<9} {'Aufrufe':<8} {'In-Tok':<9} {'Out-Tok':<9}",
         "-" * 78]
    for e in ergebnisse:
        z.append(f"{e['variante']:<10} "
                 f"{('BESTANDEN' if e['ok'] else 'NICHT BEST.'):<16} "
                 f"{e['felder']:<8} {e['dateien']:<9} {e['dauer_s']:<9.1f} "
                 f"{e['aufrufe']:<8} {e['verbrauch']['input_tokens']:<9} "
                 f"{e['verbrauch']['output_tokens']:<9}")
        if e["fehler"]:
            z.append(f"           FEHLER: {e['fehler']}")
    n_ok = sum(1 for e in ergebnisse if e["ok"])
    sum_in = sum(e["verbrauch"]["input_tokens"] for e in ergebnisse)
    sum_out = sum(e["verbrauch"]["output_tokens"] for e in ergebnisse)
    sum_cw = sum(e["verbrauch"]["cache_creation_input_tokens"] for e in ergebnisse)
    sum_cr = sum(e["verbrauch"]["cache_read_input_tokens"] for e in ergebnisse)
    sum_t = sum(e["dauer_s"] for e in ergebnisse)
    sum_a = sum(e["aufrufe"] for e in ergebnisse)
    z += ["-" * 78,
          f"GESAMT: bestanden {n_ok}/{len(ergebnisse)} | Zeit {sum_t:.1f} s | "
          f"API-Aufrufe {sum_a}",
          f"TOKENS: input {sum_in} | output {sum_out} | "
          f"cache_creation {sum_cw} | cache_read {sum_cr}",
          "",
          "Details je Variante: <Variante>/agent_log.txt und <Variante>/pruefung.txt", ""]
    (lauf_dir / "report.txt").write_text("\n".join(z), encoding="utf-8")


def selbsttest(log=print) -> bool:
    """Prueft Harness ohne API: Tool anwenden -> Pruefung muss BESTANDEN sein."""
    stempel = datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")
    tdir = BASIS / "results" / "selbsttest" / stempel
    projekt = tdir / "project"
    shutil.copytree(VORLAGE, projekt)

    vj = projekt / "variant.json"
    vj.write_text(vj.read_text(encoding="utf-8").replace("Variantx", "Entry"),
                  encoding="utf-8")
    r = subprocess.run([sys.executable, str(projekt / "tools" / "apply_variant.py")],
                       cwd=str(projekt), capture_output=True, text=True, timeout=60)
    log(r.stdout.strip())
    ok, bericht, *_ = pruefe_variante(projekt, VORLAGE, "Entry")
    (tdir / "pruefung.txt").write_text(bericht, encoding="utf-8")

    # Gegentest: unveraenderte Kopie darf NICHT bestehen
    projekt2 = tdir / "project_unveraendert"
    shutil.copytree(VORLAGE, projekt2)
    ok2, *_ = pruefe_variante(projekt2, VORLAGE, "Entry")

    erfolg = ok and not ok2
    log(f"Selbsttest: Tool-Lauf bestanden={ok}, "
        f"unveraenderte Kopie faellt durch={not ok2} -> "
        f"{'ERFOLG' if erfolg else 'FEHLGESCHLAGEN'}")
    log(f"Details: {tdir / 'pruefung.txt'}")
    return erfolg
