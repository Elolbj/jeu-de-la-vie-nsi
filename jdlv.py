"""
Module jdlv : définit la classe Jdlv, qui représente le jeu de la vie.

Un jeu contient un tableau à deux dimensions (liste de listes) de Cellule
et un compteur de tours. On crée un jeu en instanciant la classe, puis on
le lance avec la méthode start() :

    jeu = Jdlv(70, 50)
    jeu.remplir_aleatoirement()
    jeu.start()
"""

import random

from cellule import Cellule
from motifs import coordonnees_motif


class Jdlv:
    """Le jeu de la vie : un tableau fini de cellules et un compteur de tours.

    Si torique vaut True, les bords sont reliés : une cellule du bord droit
    a pour voisines les cellules du bord gauche (et de même haut/bas).
    Le tableau se comporte alors comme la surface d'un donut (un tore).
    """

    def __init__(self, largeur=70, hauteur=50, torique=True):
        assert largeur >= 3 and hauteur >= 3, "le tableau doit faire au moins 3x3"
        self.largeur = largeur
        self.hauteur = hauteur
        self.torique = torique
        self.tour = 0
        # self.grille[y][x] : y = numéro de ligne, x = numéro de colonne
        self.grille = [[Cellule() for x in range(largeur)] for y in range(hauteur)]
        self._relier_voisines()

    # ------------------------------------------------------------------
    # Construction du voisinage
    # ------------------------------------------------------------------
    def _relier_voisines(self):
        """Donne à chaque cellule la liste de ses (au plus 8) voisines."""
        for y in range(self.hauteur):
            for x in range(self.largeur):
                cellule = self.grille[y][x]
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
                            continue  # pas de voisine en dehors du tableau
                        cellule.ajouter_voisine(self.grille[vy][vx])

    def changer_torique(self, torique):
        """Active ou désactive les bords reliés, puis recalcule les voisinages."""
        self.torique = torique
        self._relier_voisines()

    # ------------------------------------------------------------------
    # Accès aux cellules
    # ------------------------------------------------------------------
    def est_dans_grille(self, x, y):
        """Renvoie True si (x, y) correspond à une case du tableau."""
        return 0 <= x < self.largeur and 0 <= y < self.hauteur

    def get_cellule(self, x, y):
        """Renvoie la cellule située colonne x, ligne y."""
        return self.grille[y][x]

    def population(self):
        """Renvoie le nombre de cellules vivantes."""
        total = 0
        for ligne in self.grille:
            for cellule in ligne:
                total += cellule.Etat
        return total

    # ------------------------------------------------------------------
    # Configuration initiale
    # ------------------------------------------------------------------
    def vider(self):
        """Tue toutes les cellules et remet le compteur de tours à 0."""
        for ligne in self.grille:
            for cellule in ligne:
                cellule.mourir()
        self.tour = 0

    def remplir_aleatoirement(self, densite=0.25):
        """Configuration aléatoire : chaque cellule a une probabilité
        `densite` d'être vivante."""
        assert 0 <= densite <= 1, "la densité est une probabilité"
        for ligne in self.grille:
            for cellule in ligne:
                if random.random() < densite:
                    cellule.naitre()
                else:
                    cellule.mourir()
        self.tour = 0

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
                self.grille[cy][cx].naitre()

    # ------------------------------------------------------------------
    # Évolution
    # ------------------------------------------------------------------
    def tour_suivant(self):
        """Fait passer tout le tableau au tour suivant.

        On procède en DEUX étapes : d'abord toutes les cellules calculent
        leur futur état, ensuite seulement elles l'appliquent. Si on
        modifiait les cellules au fur et à mesure, les voisines déjà mises
        à jour fausseraient le calcul des suivantes.
        """
        for ligne in self.grille:
            for cellule in ligne:
                cellule.calculer_etat_suivant()
        for ligne in self.grille:
            for cellule in ligne:
                cellule.passer_a_l_etat_suivant()
        self.tour += 1

    def start(self, affichage="tkinter"):
        """Lance le jeu avec l'affichage choisi : "tkinter" (fenêtre graphique)
        ou "console" (texte dans le terminal)."""
        # Les imports sont faits ici pour ne charger Tkinter que s'il sert.
        if affichage == "console":
            from jdlv_ihm_console import Jdlv_IHM_Console
            ihm = Jdlv_IHM_Console(self)
        else:
            from jdlv_ihm import Jdlv_IHM
            ihm = Jdlv_IHM(self)
        ihm.lancer()

    def __str__(self):
        """Représentation texte du tableau (utile en console et pour les tests)."""
        lignes = []
        for ligne in self.grille:
            lignes.append("".join(str(cellule) for cellule in ligne))
        return "\n".join(lignes)
