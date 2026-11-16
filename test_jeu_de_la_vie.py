"""
Tests du jeu de la vie.

Lancement : python test_jeu_de_la_vie.py   (ou : python -m pytest)
"""

from cellule import Cellule
from grille import Grille
from motifs import MOTIFS


def grille_avec(motif, x, y, largeur=10, hauteur=10, torique=False):
    grille = Grille(largeur, hauteur, torique)
    grille.placer_motif(motif, x, y)
    return grille


def cases_vivantes(grille):
    return {(x, y) for y in range(grille.hauteur) for x in range(grille.largeur)
            if grille.get_cellule(x, y).est_vivante()}


def test_regles_cellule():
    def cellule_avec(vivante, nb_voisines_vivantes):
        c = Cellule(vivante)
        for i in range(8):
            c.ajouter_voisine(Cellule(i < nb_voisines_vivantes))
        c.calculer_etat_suivant()
        return c.etat_suivant

    assert cellule_avec(False, 3) is True       # naissance
    assert cellule_avec(False, 2) is False
    assert cellule_avec(True, 2) is True        # survie
    assert cellule_avec(True, 3) is True
    assert cellule_avec(True, 1) is False       # isolement
    assert cellule_avec(True, 4) is False       # surpopulation


def test_nombre_de_voisines():
    assert len(Grille(5, 5, torique=False).get_cellule(0, 0).voisines) == 3
    assert len(Grille(5, 5, torique=False).get_cellule(2, 0).voisines) == 5
    assert len(Grille(5, 5, torique=False).get_cellule(2, 2).voisines) == 8
    assert len(Grille(5, 5, torique=True).get_cellule(0, 0).voisines) == 8


def test_bloc_stable():
    grille = grille_avec(["OO", "OO"], 4, 4)
    avant = cases_vivantes(grille)
    grille.generation_suivante()
    assert cases_vivantes(grille) == avant


def test_clignotant_periode_2():
    grille = grille_avec(MOTIFS["Clignotant"], 3, 4)
    horizontal = cases_vivantes(grille)
    grille.generation_suivante()
    assert cases_vivantes(grille) == {(4, 3), (4, 4), (4, 5)}  # vertical
    grille.generation_suivante()
    assert cases_vivantes(grille) == horizontal


def test_planeur_se_deplace():
    grille = grille_avec(MOTIFS["Planeur"], 1, 1)
    depart = cases_vivantes(grille)
    for _ in range(4):
        grille.generation_suivante()
    # Après 4 générations, le planeur s'est décalé d'une case en diagonale.
    assert cases_vivantes(grille) == {(x + 1, y + 1) for x, y in depart}
    assert grille.generation == 4


def test_planeur_traverse_les_bords_du_tore():
    grille = grille_avec(MOTIFS["Planeur"], 0, 0, largeur=8, hauteur=8, torique=True)
    depart = cases_vivantes(grille)
    for _ in range(4 * 8):  # 8 décalages de 1 case = un tour complet
        grille.generation_suivante()
    assert cases_vivantes(grille) == depart


def test_vider_et_population():
    grille = grille_avec(MOTIFS["Pulsar"], 0, 0, largeur=15, hauteur=15)
    assert grille.population() == 48
    grille.vider()
    assert grille.population() == 0
    assert grille.generation == 0


def test_canon_de_gosper_produit_des_planeurs():
    grille = grille_avec(MOTIFS["Canon de Gosper"], 1, 1, largeur=60, hauteur=40)
    population_initiale = grille.population()   # 36 cellules
    for _ in range(120):
        grille.generation_suivante()
    # Le canon a produit 4 planeurs de 5 cellules chacun.
    assert grille.population() == population_initiale + 4 * 5


if __name__ == "__main__":
    tests = [f for nom, f in list(globals().items()) if nom.startswith("test_")]
    for test in tests:
        test()
        print("OK  ", test.__name__)
    print(f"\n{len(tests)} tests réussis.")
