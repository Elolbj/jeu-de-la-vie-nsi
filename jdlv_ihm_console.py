"""
Module jdlv_ihm_console : affichage du jeu de la vie dans le terminal.

La classe Jdlv_IHM_Console offre les mêmes méthodes que Jdlv_IHM
(afficher, lancer) : Jdlv.start() peut donc utiliser l'une ou l'autre.
"""

import os
import time


class Jdlv_IHM_Console:
    """Affiche le jeu dans le terminal, en effaçant l'écran à chaque tour."""

    CARACTERE_VIVANTE = "■ "
    CARACTERE_MORTE = "· "

    def __init__(self, jeu, delai=0.15, nb_tours_max=500):
        self.jeu = jeu
        self.delai = delai                # pause entre deux tours (secondes)
        self.nb_tours_max = nb_tours_max

    def effacer_ecran(self):
        os.system("cls" if os.name == "nt" else "clear")

    def afficher(self):
        """Affiche le tableau et les statistiques."""
        self.effacer_ecran()
        for ligne in self.jeu.grille:
            texte = ""
            for cellule in ligne:
                if cellule.est_vivante():
                    texte += self.CARACTERE_VIVANTE
                else:
                    texte += self.CARACTERE_MORTE
            print(texte)
        print(f"Tour {self.jeu.tour} - population {self.jeu.population()}"
              "   (Ctrl+C pour arrêter)")

    def lancer(self):
        """Boucle principale : afficher, attendre, passer au tour suivant."""
        try:
            while self.jeu.tour < self.nb_tours_max:
                self.afficher()
                time.sleep(self.delai)
                self.jeu.tour_suivant()
            self.afficher()
        except KeyboardInterrupt:
            print("\nSimulation arrêtée.")
