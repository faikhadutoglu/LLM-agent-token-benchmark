"""Kommandozeilen-Start des Methodik-Tests.

Beispiele:
  python run_test.py --selftest      Harness ohne API pruefen
  python run_test.py --method 2      nur Methode 2 (5 Varianten-Laeufe)
  python run_test.py --all           alle 4 Methoden nacheinander
"""
import argparse

from runner.runner import run_methode, selbsttest


def main() -> None:
    p = argparse.ArgumentParser(description="TESTFAIKMETHODIK - Methodenvergleich")
    p.add_argument("--method", "-m", type=int, choices=[1, 2, 3, 4],
                   help="Nur diese Methode ausfuehren")
    p.add_argument("--all", action="store_true", help="Alle 4 Methoden nacheinander")
    p.add_argument("--selftest", action="store_true",
                   help="Harness ohne API pruefen (Tool + Referenzpruefung)")
    args = p.parse_args()

    if args.selftest:
        selbsttest()
    elif args.all:
        for nr in (1, 2, 3, 4):
            run_methode(nr)
    elif args.method:
        run_methode(args.method)
    else:
        p.print_help()


if __name__ == "__main__":
    main()
