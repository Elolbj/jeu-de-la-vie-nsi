"""
Jeu de la vie de John Horton Conway (1970) — projet POO, Terminale NSI.

Lancement :
    python main.py            -> fenêtre graphique (Tkinter)
    python main.py 220 140    -> fenêtre graphique, tableau de 220 x 140 cases
    python main.py --console  -> affichage dans le terminal
"""

import sys

from jdlv import Jdlv
from motifs import MOTIFS


def main():
    """Crée le jeu de départ et le lance en mode graphique ou console."""
    if "--console" in sys.argv:
        jeu = Jdlv(40, 20, torique=True)
        jeu.remplir_aleatoirement(0.3)
        jeu.start("console")
    else:
        nombres = [int(argument) for argument in sys.argv[1:] if argument.isdigit()]
        largeur, hauteur = nombres[:2] if len(nombres) >= 2 else (70, 45)
        jeu = Jdlv(largeur, hauteur, torique=False)
        jeu.placer_motif(MOTIFS["Canon de Gosper"], 2, 2)
        jeu.start("tkinter")


if __name__ == "__main__":
    main()
