"""
Module cellule : définit la classe Cellule du jeu de la vie.

Une cellule possède un attribut Etat (entier) : 0 = morte, 1 = vivante.
Elle connaît ses voisines, ce qui lui permet de calculer elle-même son état
au tour suivant.
"""

MORTE = 0
VIVANTE = 1


class Cellule:
    """Une case du tableau du jeu de la vie."""

    def __init__(self, etat=MORTE):
        assert etat in (MORTE, VIVANTE), "l'état d'une cellule vaut 0 ou 1"
        self.Etat = etat              # état actuel : 0 (morte) ou 1 (vivante)
        self.etat_suivant = etat      # état calculé pour le tour suivant
        self.voisines = []            # liste des cellules voisines (au plus 8)

    # ------------------------------------------------------------------
    # Accès et modification de l'état
    # ------------------------------------------------------------------
    def est_vivante(self):
        """Renvoie True si la cellule est vivante."""
        return self.Etat == VIVANTE

    def naitre(self):
        """Rend la cellule vivante."""
        self.Etat = VIVANTE

    def mourir(self):
        """Rend la cellule morte."""
        self.Etat = MORTE

    def basculer(self):
        """Inverse l'état de la cellule (0 <-> 1)."""
        self.Etat = 1 - self.Etat

    # ------------------------------------------------------------------
    # Voisinage
    # ------------------------------------------------------------------
    def ajouter_voisine(self, cellule):
        """Ajoute une cellule à la liste des voisines."""
        self.voisines.append(cellule)

    def nombre_voisines_vivantes(self):
        """Compte les voisines vivantes.

        Comme Etat vaut 0 ou 1, il suffit d'additionner les états des voisines.
        """
        total = 0
        for voisine in self.voisines:
            total += voisine.Etat
        return total

    # ------------------------------------------------------------------
    # Règles de Conway
    # ------------------------------------------------------------------
    def calculer_etat_suivant(self):
        """Calcule (sans l'appliquer) l'état de la cellule au tour suivant.

        Règles de John Horton Conway :
          - une cellule morte avec exactement 3 voisines vivantes naît ;
          - une cellule vivante avec 2 ou 3 voisines vivantes survit ;
          - dans tous les autres cas, la cellule meurt ou reste morte.
        """
        n = self.nombre_voisines_vivantes()
        if self.est_vivante():
            if n == 2 or n == 3:
                self.etat_suivant = VIVANTE
            else:
                self.etat_suivant = MORTE
        else:
            if n == 3:
                self.etat_suivant = VIVANTE
            else:
                self.etat_suivant = MORTE

    def passer_a_l_etat_suivant(self):
        """Applique l'état calculé par calculer_etat_suivant()."""
        self.Etat = self.etat_suivant

    def __str__(self):
        return "#" if self.est_vivante() else "."
