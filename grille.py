"""
Module grille : définit la classe Grille, qui contient toutes les cellules
et fait évoluer le jeu de génération en génération.
"""

import random

from cellule import Cellule
from motifs import coordonnees_motif


class Grille:
    """Grille rectangulaire de cellules.

    Si torique vaut True, les bords sont reliés : une cellule du bord droit
    a pour voisines les cellules du bord gauche (et de même haut/bas).
    La grille se comporte alors comme la surface d'un donut (un tore).
    """

    def __init__(self, largeur, hauteur, torique=True):
        assert largeur >= 3 and hauteur >= 3, "la grille doit faire au moins 3x3"
        self.largeur = largeur
        self.hauteur = hauteur
        self.torique = torique
        self.generation = 0
        # self.cellules[y][x] : y = numéro de ligne, x = numéro de colonne
        self.cellules = [[Cellule() for x in range(largeur)] for y in range(hauteur)]
        self._relier_voisines()

    # ------------------------------------------------------------------
    # Construction du voisinage
    # ------------------------------------------------------------------
    def _relier_voisines(self):
        """Donne à chaque cellule la liste de ses (au plus 8) voisines."""
        for y in range(self.hauteur):
            for x in range(self.largeur):
                cellule = self.cellules[y][x]
                cellule.voisines = []
                for dy in (-1, 0, 1):
                    for dx in (-1, 0, 1):
                        if dx == 0 and dy == 0:
                            continue  # une cellule n'est pas sa propre voisine
                        vx = x + dx
                        vy = y + dy
                        if self.torique:
                            vx = vx % self.largeur
                            vy = vy % self.hauteur
                        elif not self.est_dans_grille(vx, vy):
                            continue  # pas de voisine en dehors de la grille
                        cellule.ajouter_voisine(self.cellules[vy][vx])

    def changer_torique(self, torique):
        """Active ou désactive les bords reliés, puis recalcule les voisinages."""
        self.torique = torique
        self._relier_voisines()

    # ------------------------------------------------------------------
    # Accès aux cellules
    # ------------------------------------------------------------------
    def est_dans_grille(self, x, y):
        """Renvoie True si (x, y) correspond à une case de la grille."""
        return 0 <= x < self.largeur and 0 <= y < self.hauteur

    def get_cellule(self, x, y):
        """Renvoie la cellule située colonne x, ligne y."""
        return self.cellules[y][x]

    def population(self):
        """Renvoie le nombre de cellules vivantes."""
        total = 0
        for ligne in self.cellules:
            for cellule in ligne:
                if cellule.est_vivante():
                    total += 1
        return total

    # ------------------------------------------------------------------
    # Modification de la grille
    # ------------------------------------------------------------------
    def vider(self):
        """Tue toutes les cellules et remet le compteur de générations à 0."""
        for ligne in self.cellules:
            for cellule in ligne:
                cellule.mourir()
        self.generation = 0

    def remplir_aleatoirement(self, densite=0.25):
        """Remplit la grille au hasard : chaque cellule a une probabilité
        `densite` d'être vivante."""
        for ligne in self.cellules:
            for cellule in ligne:
                if random.random() < densite:
                    cellule.naitre()
                else:
                    cellule.mourir()
        self.generation = 0

    def placer_motif(self, motif, x, y):
        """Place un motif (liste de chaînes, voir motifs.py) en prenant
        (x, y) comme coin supérieur gauche."""
        for dx, dy in coordonnees_motif(motif):
            cx = x + dx
            cy = y + dy
            if self.torique:
                cx = cx % self.largeur
                cy = cy % self.hauteur
            if self.est_dans_grille(cx, cy):
                self.cellules[cy][cx].naitre()

    # ------------------------------------------------------------------
    # Évolution
    # ------------------------------------------------------------------
    def generation_suivante(self):
        """Fait passer toute la grille à la génération suivante.

        On procède en DEUX étapes : d'abord toutes les cellules calculent
        leur futur état, ensuite seulement elles l'appliquent. Si on
        modifiait les cellules au fur et à mesure, les voisines déjà mises
        à jour fausseraient le calcul des suivantes.
        """
        for ligne in self.cellules:
            for cellule in ligne:
                cellule.calculer_etat_suivant()
        for ligne in self.cellules:
            for cellule in ligne:
                cellule.passer_a_l_etat_suivant()
        self.generation += 1

    def __str__(self):
        """Représentation texte de la grille (utile en console et pour les tests)."""
        lignes = []
        for ligne in self.cellules:
            lignes.append("".join(str(cellule) for cellule in ligne))
        return "\n".join(lignes)
