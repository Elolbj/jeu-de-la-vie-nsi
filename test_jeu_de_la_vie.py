"""
Tests du jeu de la vie.

Lancement : python test_jeu_de_la_vie.py   (ou : python -m pytest)
"""

from cellule import Cellule
from jdlv import CYCLE, EN_EVOLUTION, EXTINCTION, STABLE, Jdlv
from motifs import MOTIFS
from regle import Regle
from rle import convertir_regle, ecrire_rle, lire_rle


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


def test_detection_stable_extinction_cycle():
    jeu = jeu_avec(["OO", "OO"], 4, 4)
    jeu.tour_suivant()
    assert jeu.statut == STABLE

    jeu = jeu_avec(["O"], 4, 4)              # une cellule seule meurt
    jeu.tour_suivant()
    assert jeu.statut == EXTINCTION

    jeu = jeu_avec(MOTIFS["Pulsar"], 1, 1, largeur=15, hauteur=15)
    for _ in range(3):
        assert jeu.statut == EN_EVOLUTION
        jeu.tour_suivant()
    assert jeu.statut == CYCLE and jeu.periode == 3


def test_retour_arriere():
    jeu = jeu_avec(MOTIFS["R-pentomino"], 20, 20, largeur=50, hauteur=50)
    depart = cases_vivantes(jeu)
    for _ in range(30):
        jeu.tour_suivant()
    for _ in range(30):
        assert jeu.tour_precedent()
    assert jeu.tour == 0
    assert cases_vivantes(jeu) == depart
    assert jeu.tour_precedent() is False     # plus d'historique
    assert jeu.populations == [5]


GOSPER_RLE = """#N Gosper glider gun (format publié sur LifeWiki)
x = 36, y = 9, rule = B3/S23
24bo$22bobo$12b2o6b2o12b2o$11bo3bo4b2o12b2o$2o8bo5bo3b2o$2o8bo3bob2o4b
obo$10bo5bo7bo$11bo3bo$12b2o!"""


def test_lecture_rle():
    motif, regle = lire_rle(GOSPER_RLE)
    assert motif == MOTIFS["Canon de Gosper"]   # nos données sont justes
    assert regle == "B3/S23"
    assert lire_rle("x = 3, y = 2\n3o$o!") == (["OOO", "O.."], None)
    assert lire_rle("x = 1, y = 3\no2$o!")[0] == ["O", ".", "O"]   # 2$ = ligne vide


def test_ecriture_rle_aller_retour():
    for nom, motif in MOTIFS.items():
        texte = ecrire_rle(motif, "B3/S23", nom)
        assert lire_rle(texte) == (motif, "B3/S23"), nom
        assert all(len(ligne) <= 70 for ligne in texte.splitlines())


def test_regles_rle_et_erreurs():
    assert convertir_regle("23/3") == "B3/S23"          # ancienne notation S/B
    assert convertir_regle("b36/s23") == "B36/S23"
    assert convertir_regle("B3/S23:T70,50") == "B3/S23"  # forme du tableau ignorée
    try:
        lire_rle("x = 3, y = 3\nbo$2bo%3o!")
        assert False, "le caractère % aurait dû être refusé"
    except ValueError:
        pass


def test_charger_et_extraire_un_motif():
    jeu = Jdlv(20, 20)
    jeu.charger_motif(MOTIFS["Planeur"], "B36/S23")
    assert jeu.motif_actuel() == MOTIFS["Planeur"] and str(jeu.regle) == "B36/S23"
    assert jeu.tour == 0 and jeu.populations == [5]
    try:
        jeu.charger_motif(MOTIFS["Canon de Gosper"])   # 36 colonnes > 20
        assert False, "motif trop grand accepté"
    except ValueError:
        assert jeu.motif_actuel() == MOTIFS["Planeur"]   # rien n'a changé


def test_pentadecathlon_et_diehard():
    jeu = Jdlv(30, 20, torique=False)
    jeu.charger_motif(MOTIFS["Pentadécathlon"])
    while jeu.statut == EN_EVOLUTION:
        jeu.tour_suivant()
    assert jeu.statut == CYCLE and jeu.periode == 15

    jeu = Jdlv(40, 40, torique=False)
    jeu.charger_motif(MOTIFS["Diehard"])
    while jeu.statut == EN_EVOLUTION:
        jeu.tour_suivant()
    assert jeu.statut == EXTINCTION and jeu.tour == 130


if __name__ == "__main__":
    tests = [f for nom, f in list(globals().items()) if nom.startswith("test_")]
    for test in tests:
        test()
        print("OK  ", test.__name__)
    print(f"\n{len(tests)} tests réussis.")
