"""
Module regle : règles des automates cellulaires « de type vie ».

Une règle s'écrit en notation B/S (Birth / Survival) :
    "B3/S23" signifie : une cellule morte NAÎT si elle a 3 voisines vivantes,
                        une cellule vivante SURVIT si elle a 2 ou 3 voisines.
C'est la règle de Conway. En changeant les chiffres, on obtient d'autres
« univers » aux comportements très différents.
"""

# Quelques règles célèbres : nom affiché -> notation B/S
REGLES = {
    "Conway": "B3/S23",
    "HighLife": "B36/S23",
    "Seeds": "B2/S",
    "Day & Night": "B3678/S34678",
    "Réplicateur": "B1357/S1357",
    "Labyrinthe": "B3/S12345",
    "34 Life": "B34/S34",
    "Vie sans mort": "B3/S012345678",
}


class Regle:
    """Règle de naissance et de survie, construite à partir de sa notation B/S."""

    def __init__(self, notation="B3/S23"):
        self.notation = notation.strip().upper()
        self.naissance, self.survie = self._analyser()

    def _analyser(self):
        """Découpe la notation "B.../S..." et renvoie deux ensembles de nombres
        de voisines : ceux qui font naître et ceux qui font survivre.

        Lève ValueError si la notation est incorrecte.
        """
        morceaux = self.notation.split("/")
        if len(morceaux) != 2 or not morceaux[0].startswith("B") \
                or not morceaux[1].startswith("S"):
            raise ValueError(f"notation invalide : {self.notation!r} (exemple : B3/S23)")
        naissance = set()
        survie = set()
        for chiffre in morceaux[0][1:]:
            naissance.add(self._nombre_de_voisines(chiffre))
        for chiffre in morceaux[1][1:]:
            survie.add(self._nombre_de_voisines(chiffre))
        return naissance, survie

    def _nombre_de_voisines(self, caractere):
        if caractere not in "012345678":
            raise ValueError(f"{caractere!r} n'est pas un nombre de voisines (0 à 8)")
        return int(caractere)

    def etat_suivant(self, etat, nb_voisines_vivantes):
        """Renvoie l'état (0 ou 1) d'une cellule au tour suivant."""
        if etat == 1:
            return 1 if nb_voisines_vivantes in self.survie else 0
        return 1 if nb_voisines_vivantes in self.naissance else 0

    def __str__(self):
        return self.notation
