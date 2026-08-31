"""GUI mit 4 Knoepfen (eine je Methode) + Selbsttest. Start: python gui.py"""
import queue
import threading
import tkinter as tk
from tkinter import scrolledtext

from runner.methods import METHODEN
from runner.runner import run_methode, selbsttest


class App:
    def __init__(self, root: tk.Tk):
        self.root = root
        root.title("TESTFAIKMETHODIK - Methodenvergleich Tischlampe")
        root.geometry("900x560")
        self.q = queue.Queue()
        self.laeuft = False

        frame = tk.Frame(root)
        frame.pack(fill=tk.X, padx=8, pady=8)
        self.knoepfe = []
        for nr in (1, 2, 3, 4):
            b = tk.Button(frame, text=METHODEN[nr]["titel"], width=26,
                          command=lambda n=nr: self.starte(lambda: run_methode(n, self.log)))
            b.grid(row=(nr - 1) // 2, column=(nr - 1) % 2, padx=4, pady=4)
            self.knoepfe.append(b)
        b = tk.Button(frame, text="Selbsttest (ohne API)", width=26,
                      command=lambda: self.starte(lambda: selbsttest(self.log)))
        b.grid(row=2, column=0, padx=4, pady=4)
        self.knoepfe.append(b)

        self.text = scrolledtext.ScrolledText(root, state=tk.DISABLED, wrap=tk.WORD)
        self.text.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0, 8))
        root.after(150, self.poll)

    def log(self, *teile):
        self.q.put(" ".join(str(t) for t in teile))

    def starte(self, funktion):
        if self.laeuft:
            self.log("Bitte warten - es laeuft bereits ein Test.")
            return
        self.laeuft = True
        for b in self.knoepfe:
            b.config(state=tk.DISABLED)

        def arbeit():
            try:
                funktion()
            except Exception as ex:
                self.log(f"FEHLER: {type(ex).__name__}: {ex}")
            finally:
                self.q.put(("__fertig__",))

        threading.Thread(target=arbeit, daemon=True).start()

    def poll(self):
        try:
            while True:
                eintrag = self.q.get_nowait()
                if eintrag == ("__fertig__",):
                    self.laeuft = False
                    for b in self.knoepfe:
                        b.config(state=tk.NORMAL)
                    self._schreibe("--- fertig ---")
                else:
                    self._schreibe(eintrag)
        except queue.Empty:
            pass
        self.root.after(150, self.poll)

    def _schreibe(self, zeile):
        self.text.config(state=tk.NORMAL)
        self.text.insert(tk.END, str(zeile) + "\n")
        self.text.see(tk.END)
        self.text.config(state=tk.DISABLED)


if __name__ == "__main__":
    root = tk.Tk()
    App(root)
    root.mainloop()
