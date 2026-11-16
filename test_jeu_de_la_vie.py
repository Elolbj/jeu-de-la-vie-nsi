"""
Tests du jeu de la vie.

Lancement : python test_jeu_de_la_vie.py   (ou : python -m pytest)
"""

from cellule import Cellule
from jdlv import Jdlv
from motifs import MOTIFS
from regle import Regle


def jeu_avec(motif, x, y, largeur=10, hauteur=10, torique=False):
    jeu = Jdlv(largeur, hauteur, torique)
    jeu.placer_motif(motif, x, y)
    return jeu


def cases_vivantes(jeu):
    return {(x, y) for y in range(jeu.hauteur) for x in range(jeu.largeur)
            if jeu.get_cellule(x, y).est_vivante()}


def test_regles_cellule():
    def cellule_avec(vivante, nb_voisines_vivantes):
        c = Cellule(vivante)
        for i in range(8):
            c.ajouter_voisine(Cellule(1 if i < nb_voisines_vivantes else 0))
        c.calculer_etat_suivant()
        return c.etat_suivant

    assert cellule_avec(0, 3) == 1   # naissance
    assert cellule_avec(0, 2) == 0
    assert cellule_avec(1, 2) == 1   # survie
    assert cellule_avec(1, 3) == 1
    assert cellule_avec(1, 1) == 0   # isolement
    assert cellule_avec(1, 4) == 0   # surpopulation


def test_nombre_de_voisines():
    assert len(Jdlv(5, 5, torique=False).get_cellule(0, 0).voisines) == 3
    assert len(Jdlv(5, 5, torique=False).get_cellule(2, 0).voisines) == 5
    assert len(Jdlv(5, 5, torique=False).get_cellule(2, 2).voisines) == 8
    assert len(Jdlv(5, 5, torique=True).get_cellule(0, 0).voisines) == 8


def test_bloc_stable():
    jeu = jeu_avec(["OO", "OO"], 4, 4)
    avant = cases_vivantes(jeu)
    jeu.tour_suivant()
    assert cases_vivantes(jeu) == avant


def test_clignotant_periode_2():
    jeu = jeu_avec(MOTIFS["Clignotant"], 3, 4)
    horizontal = cases_vivantes(jeu)
    jeu.tour_suivant()
    assert cases_vivantes(jeu) == {(4, 3), (4, 4), (4, 5)}  # vertical
    jeu.tour_suivant()
    assert cases_vivantes(jeu) == horizontal


def test_planeur_se_deplace():
    jeu = jeu_avec(MOTIFS["Planeur"], 1, 1)
    depart = cases_vivantes(jeu)
    for _ in range(4):
        jeu.tour_suivant()
    # Après 4 générations, le planeur s'est décalé d'une case en diagonale.
    assert cases_vivantes(jeu) == {(x + 1, y + 1) for x, y in depart}
    assert jeu.tour == 4


def test_planeur_traverse_les_bords_du_tore():
    jeu = jeu_avec(MOTIFS["Planeur"], 0, 0, largeur=8, hauteur=8, torique=True)
    depart = cases_vivantes(jeu)
    for _ in range(4 * 8):  # 8 décalages de 1 case = un tour complet
        jeu.tour_suivant()
    assert cases_vivantes(jeu) == depart


def test_vider_et_population():
    jeu = jeu_avec(MOTIFS["Pulsar"], 0, 0, largeur=15, hauteur=15)
    assert jeu.population() == 48
    jeu.vider()
    assert jeu.population() == 0
    assert jeu.tour == 0


def test_canon_de_gosper_produit_des_planeurs():
    jeu = jeu_avec(MOTIFS["Canon de Gosper"], 1, 1, largeur=60, hauteur=40)
    population_initiale = jeu.population()   # 36 cellules
    for _ in range(120):
        jeu.tour_suivant()
    # Le canon a produit 4 planeurs de 5 cellules chacun.
    assert jeu.population() == population_initiale + 4 * 5


def test_notation_des_regles():
    regle = Regle("b36/s23")
    assert regle.naissance == {3, 6} and regle.survie == {2, 3}
    assert Regle("B2/S").survie == set()          # Seeds : aucune survie
    for notation_invalide in ["B3S23", "X3/S23", "B9/S23", "B3/23", ""]:
        try:
            Regle(notation_invalide)
            assert False, f"{notation_invalide!r} aurait dû être refusée"
        except ValueError:
            pass


def test_seeds_aucune_cellule_ne_survit():
    jeu = jeu_avec(["OO", "OO"], 4, 4)   # un bloc, stable avec Conway...
    jeu.changer_regle("B2/S")
    avant = cases_vivantes(jeu)
    jeu.tour_suivant()
    assert cases_vivantes(jeu).isdisjoint(avant)  # ... mais pas avec Seeds


def test_age_des_cellules():
    jeu = jeu_avec(MOTIFS["Clignotant"], 3, 4)
    centre = jeu.get_cellule(4, 4)          # la case du milieu ne meurt jamais
    for _ in range(3):
        jeu.tour_suivant()
    assert centre.age == 4
    assert jeu.get_cellule(3, 4).age == 0   # extrémité : morte au tour 3
    centre.mourir()
    assert centre.age == 0 and centre.Etat == 0


if __name__ == "__main__":
    tests = [f for nom, f in list(globals().items()) if nom.startswith("test_")]
    for test in tests:
        test()
        print("OK  ", test.__name__)
    print(f"\n{len(tests)} tests réussis.")
