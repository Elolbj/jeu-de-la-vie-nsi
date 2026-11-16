"""
Jeu de la vie de John Horton Conway (1970) — projet POO, Terminale NSI.

Lancement :
    python main.py            -> fenêtre graphique (Tkinter), taille adaptée à la machine
    python main.py 220 140    -> fenêtre graphique, tableau de 220 x 140 cases
    python main.py --console  -> affichage dans le terminal
"""

import shutil
import sys

from jdlv import Jdlv
from materiel import Materiel
from motifs import MOTIFS


def main():
    """Détecte le matériel, crée le jeu de départ et le lance (fenêtre ou console)."""
    materiel = Materiel.detecter()
    # La mémoire du retour arrière s'adapte à la mémoire vive de la machine
    Jdlv.BUDGET_HISTORIQUE = materiel.budget_historique()

    if "--console" in sys.argv:
        # Le tableau prend la taille du terminal (2 caractères par case)
        colonnes, lignes = shutil.get_terminal_size((80, 24))
        jeu = Jdlv(max(10, colonnes // 2), max(5, lignes - 3), torique=True)
        jeu.remplir_aleatoirement(0.3)
        jeu.start("console")
    else:
        nombres = [int(argument) for argument in sys.argv[1:] if argument.isdigit()]
        if len(nombres) >= 2:
            largeur, hauteur = nombres[:2]
        else:
            largeur, hauteur = materiel.taille_de_depart()   # selon l'écran et la vitesse
        jeu = Jdlv(largeur, hauteur, torique=False)
        jeu.placer_motif(MOTIFS["Canon de Gosper"], 2, 2)
        jeu.start("tkinter")


if __name__ == "__main__":
    main()
