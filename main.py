"""
Jeu de la vie de John Horton Conway (1970) — projet POO, Terminale NSI.

Lancement :
    python main.py            -> fenêtre graphique (Tkinter)
    python main.py --console  -> affichage dans le terminal
"""

import sys

from jdlv import Jdlv
from motifs import MOTIFS


def main():
    if "--console" in sys.argv:
        jeu = Jdlv(40, 20, torique=True)
        jeu.remplir_aleatoirement(0.3)
        jeu.start("console")
    else:
        jeu = Jdlv(70, 50, torique=False)
        jeu.placer_motif(MOTIFS["Canon de Gosper"], 2, 2)
        jeu.start("tkinter")


if __name__ == "__main__":
    main()
