"""
Module cellule : définit la classe Cellule du jeu de la vie.

Une cellule possède un attribut Etat (entier) : 0 = morte, 1 = vivante.
Elle connaît ses voisines, ce qui lui permet de calculer elle-même son état
au tour suivant.
"""

from regle import Regle

MORTE = 0
VIVANTE = 1
CONWAY = Regle("B3/S23")


class Cellule:
    """Une case du tableau du jeu de la vie."""

    def __init__(self, etat=MORTE):
        assert etat in (MORTE, VIVANTE), "l'état d'une cellule vaut 0 ou 1"
        self.Etat = etat              # état actuel : 0 (morte) ou 1 (vivante)
        self.etat_suivant = etat      # état calculé pour le tour suivant
        self.age = etat               # nombre de tours consécutifs en vie (0 si morte)
        self.voisines = []            # liste des cellules voisines (au plus 8)

    # ------------------------------------------------------------------
    # Accès et modification de l'état
    # ------------------------------------------------------------------
    def est_vivante(self):
        """Renvoie True si la cellule est vivante."""
        return self.Etat == VIVANTE

    def naitre(self):
        """Rend la cellule vivante (si elle l'était déjà, son âge ne change pas)."""
        if not self.est_vivante():
            self.Etat = VIVANTE
            self.age = 1

    def mourir(self):
        """Rend la cellule morte."""
        self.Etat = MORTE
        self.age = 0

    def basculer(self):
        """Inverse l'état de la cellule (0 <-> 1)."""
        if self.est_vivante():
            self.mourir()
        else:
            self.naitre()

    # ------------------------------------------------------------------
    # Voisinage
    # ------------------------------------------------------------------
    def ajouter_voisine(self, cellule):
        """Ajoute une cellule à la liste des voisines."""
        self.voisines.append(cellule)

    def nombre_voisines_vivantes(self):
        """Compte les voisines vivantes.

        Comme Etat vaut 0 ou 1, il suffit d'additionner les états des voisines.

        >>> c = Cellule()
        >>> for etat in [1, 1, 0, 1]:
        ...     c.ajouter_voisine(Cellule(etat))
        >>> c.nombre_voisines_vivantes()
        3
        """
        total = 0
        for voisine in self.voisines:
            total += voisine.Etat
        return total

    # ------------------------------------------------------------------
    # Règles de Conway
    # ------------------------------------------------------------------
    def calculer_etat_suivant(self, regle=CONWAY):
        """Calcule (sans l'appliquer) l'état de la cellule au tour suivant.

        Par défaut, ce sont les règles de John Horton Conway (B3/S23) :
          - une cellule morte avec exactement 3 voisines vivantes naît ;
          - une cellule vivante avec 2 ou 3 voisines vivantes survit ;
          - dans tous les autres cas, la cellule meurt ou reste morte.
        On peut passer une autre Regle (voir regle.py) pour changer d'univers.
        """
        n = self.nombre_voisines_vivantes()
        self.etat_suivant = regle.etat_suivant(self.Etat, n)

    def passer_a_l_etat_suivant(self):
        """Applique l'état calculé par calculer_etat_suivant() et met l'âge à jour."""
        if self.etat_suivant == VIVANTE:
            self.age += 1     # une cellule qui naît passe de l'âge 0 à 1
        else:
            self.age = 0
        self.Etat = self.etat_suivant

    def __str__(self):
        return "#" if self.est_vivante() else "."
