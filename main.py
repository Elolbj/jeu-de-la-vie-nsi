"""
Jeu de la vie de John Horton Conway (1970) — projet NSI.

Lancement :
    python main.py            -> fenêtre graphique (Tkinter)
    python main.py --console  -> affichage dans le terminal
"""

import sys
import time

from grille import Grille
from motifs import MOTIFS

LARGEUR = 70   # nombre de colonnes
HAUTEUR = 50   # nombre de lignes


def lancer_graphique():
    from affichage import FenetreJeu  # importé ici : Tkinter n'est utile qu'en mode graphique

    grille = Grille(LARGEUR, HAUTEUR, torique=False)
    grille.placer_motif(MOTIFS["Canon de Gosper"], 2, 2)
    fenetre = FenetreJeu(grille, taille_cellule=12)
    fenetre.lancer()


def lancer_console(nb_generations=200):
    grille = Grille(40, 20, torique=True)
    grille.remplir_aleatoirement(0.3)
    for _ in range(nb_generations):
        print("\033[H\033[J", end="")  # efface le terminal
        print(grille)
        print(f"Génération {grille.generation} - population {grille.population()}")
        grille.generation_suivante()
        time.sleep(0.1)


if __name__ == "__main__":
    if "--console" in sys.argv:
        lancer_console()
    else:
        lancer_graphique()
