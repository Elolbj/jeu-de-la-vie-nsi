"""
Module cellule : définit la classe Cellule du jeu de la vie.

Une cellule est soit vivante, soit morte. Elle connaît ses voisines,
ce qui lui permet de calculer elle-même son état à la génération suivante.
"""


class Cellule:
    """Une case de la grille du jeu de la vie."""

    def __init__(self, vivante=False):
        self.vivante = vivante        # état actuel (True = vivante)
        self.etat_suivant = vivante   # état calculé pour la prochaine génération
        self.voisines = []            # liste des cellules voisines (au plus 8)

    # ------------------------------------------------------------------
    # Accès et modification de l'état
    # ------------------------------------------------------------------
    def est_vivante(self):
        """Renvoie True si la cellule est vivante."""
        return self.vivante

    def naitre(self):
        """Rend la cellule vivante."""
        self.vivante = True

    def mourir(self):
        """Rend la cellule morte."""
        self.vivante = False

    def basculer(self):
        """Inverse l'état de la cellule (vivante <-> morte)."""
        self.vivante = not self.vivante

    # ------------------------------------------------------------------
    # Voisinage
    # ------------------------------------------------------------------
    def ajouter_voisine(self, cellule):
        """Ajoute une cellule à la liste des voisines."""
        self.voisines.append(cellule)

    def nombre_voisines_vivantes(self):
        """Compte les voisines vivantes."""
        compteur = 0
        for voisine in self.voisines:
            if voisine.est_vivante():
                compteur += 1
        return compteur

    # ------------------------------------------------------------------
    # Règles de Conway
    # ------------------------------------------------------------------
    def calculer_etat_suivant(self):
        """Calcule (sans l'appliquer) l'état de la cellule à la génération suivante.

        Règles de John Horton Conway :
          - une cellule morte avec exactement 3 voisines vivantes naît ;
          - une cellule vivante avec 2 ou 3 voisines vivantes survit ;
          - dans tous les autres cas, la cellule meurt ou reste morte.
        """
        n = self.nombre_voisines_vivantes()
        if self.vivante:
            self.etat_suivant = (n == 2 or n == 3)
        else:
            self.etat_suivant = (n == 3)

    def passer_a_l_etat_suivant(self):
        """Applique l'état calculé par calculer_etat_suivant()."""
        self.vivante = self.etat_suivant

    def __str__(self):
        return "#" if self.vivante else "."
