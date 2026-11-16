"""
Tests du jeu de la vie.

Lancement :  python test_jeu_de_la_vie.py      (ou : python -m pytest)

Les tests sont regroupés par thème :
  1. conformité au sujet (noms des classes et des attributs imposés)
  2. règles d'une cellule (les 18 cas possibles) et notation B/S
  3. voisinage et bords (tableau fini ou torique)
  4. motifs connus (stable, oscillateurs, vaisseaux, canon, mathusalems)
  5. comparaison avec une implémentation de référence indépendante
  6. historique et détection des cycles
  7. format de fichier RLE
  8. affichage console
  9. exemples des docstrings (doctests)
Les nombres attendus (périodes, tour 130 du diehard...) viennent de LifeWiki.
"""

import doctest
import io
import random
from contextlib import redirect_stdout

from cellule import Cellule
from jdlv import CYCLE, EN_EVOLUTION, EXTINCTION, STABLE, Jdlv
from jdlv_ihm_console import Jdlv_IHM_Console
from motifs import MOTIFS
from regle import REGLES, Regle
from rle import convertir_regle, ecrire_rle, lire_rle


# ----------------------------------------------------------------------
# Fonctions utilitaires
# ----------------------------------------------------------------------
def jeu_avec(motif, x, y, largeur=10, hauteur=10, torique=False):
    """Crée un jeu contenant un motif placé en (x, y)."""
    jeu = Jdlv(largeur, hauteur, torique)
    jeu.placer_motif(motif, x, y)
    return jeu


def cases_vivantes(jeu):
    """Ensemble des coordonnées (x, y) des cellules vivantes."""
    return {(x, y) for y in range(jeu.hauteur) for x in range(jeu.largeur)
            if jeu.get_cellule(x, y).est_vivante()}


def avancer_jusqu_a_stabilisation(jeu, tours_max=5000):
    while jeu.statut == EN_EVOLUTION and jeu.tour < tours_max:
        jeu.tour_suivant()


def doit_echouer(fonction, *arguments):
    """Vérifie que fonction(*arguments) lève une erreur (ValueError ou AssertionError)."""
    try:
        fonction(*arguments)
    except (ValueError, AssertionError):
        return
    raise AssertionError(f"{fonction.__name__}{arguments} aurait dû échouer")


# ----------------------------------------------------------------------
# 1. Conformité au sujet
# ----------------------------------------------------------------------
def test_conformite_au_sujet():
    cellule = Cellule()
    assert isinstance(cellule.Etat, int) and cellule.Etat == 0   # morte par défaut
    assert Cellule(1).Etat == 1                                   # vivante
    jeu = Jdlv(5, 4)
    assert jeu.tour == 0
    assert isinstance(jeu.grille, list) and len(jeu.grille) == 4  # liste de listes
    for ligne in jeu.grille:
        assert isinstance(ligne, list) and len(ligne) == 5
        assert all(isinstance(c, Cellule) for c in ligne)
    assert callable(jeu.start)


def test_entrees_invalides():
    doit_echouer(Cellule, 2)              # Etat vaut 0 ou 1
    doit_echouer(Jdlv, 2, 10)             # tableau d'au moins 3x3
    doit_echouer(Jdlv(5, 5).remplir_aleatoirement, 1.5)


# ----------------------------------------------------------------------
# 2. Règles
# ----------------------------------------------------------------------
def etat_suivant(etat, nb_voisines_vivantes, regle=None):
    """État au tour suivant d'une cellule entourée de 8 voisines dont
    nb_voisines_vivantes sont vivantes."""
    cellule = Cellule(etat)
    for i in range(8):
        cellule.ajouter_voisine(Cellule(1 if i < nb_voisines_vivantes else 0))
    if regle is None:
        cellule.calculer_etat_suivant()
    else:
        cellule.calculer_etat_suivant(regle)
    return cellule.etat_suivant


def test_les_18_cas_de_la_regle_de_conway():
    for etat in (0, 1):
        for n in range(9):
            naissance = (etat == 0 and n == 3)
            survie = (etat == 1 and n in (2, 3))
            attendu = 1 if naissance or survie else 0
            assert etat_suivant(etat, n) == attendu, (etat, n)


def test_notation_des_regles():
    regle = Regle("b36/s23")
    assert regle.naissance == {3, 6} and regle.survie == {2, 3}
    assert Regle("B2/S").survie == set()           # Seeds : aucune survie
    assert etat_suivant(0, 6, regle) == 1            # HighLife : naissance avec 6
    for notation in REGLES.values():                 # toutes les règles proposées sont valides
        assert str(Regle(notation)) == notation
    for notation_invalide in ["B3S23", "X3/S23", "B9/S23", "B3/23", ""]:
        doit_echouer(Regle, notation_invalide)


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


# ----------------------------------------------------------------------
# 3. Voisinage et bords
# ----------------------------------------------------------------------
def test_nombre_de_voisines():
    assert len(Jdlv(5, 5, torique=False).get_cellule(0, 0).voisines) == 3   # coin
    assert len(Jdlv(5, 5, torique=False).get_cellule(2, 0).voisines) == 5   # bord
    assert len(Jdlv(5, 5, torique=False).get_cellule(2, 2).voisines) == 8   # milieu
    assert len(Jdlv(5, 5, torique=True).get_cellule(0, 0).voisines) == 8    # tore


def test_planeur_traverse_les_bords_du_tore():
    jeu = jeu_avec(MOTIFS["Planeur"], 0, 0, largeur=8, hauteur=8, torique=True)
    depart = cases_vivantes(jeu)
    for _ in range(4 * 8):  # 8 décalages d'une case = un tour complet
        jeu.tour_suivant()
    assert cases_vivantes(jeu) == depart


def test_planeur_devient_un_bloc_contre_un_bord():
    jeu = jeu_avec(MOTIFS["Planeur"], 0, 0, largeur=8, hauteur=8, torique=False)
    avancer_jusqu_a_stabilisation(jeu)
    assert jeu.statut == STABLE and jeu.population() == 4


# ----------------------------------------------------------------------
# 4. Motifs connus
# ----------------------------------------------------------------------
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
    # Après 4 tours, le planeur s'est décalé d'une case en diagonale.
    assert cases_vivantes(jeu) == {(x + 1, y + 1) for x, y in depart}
    assert jeu.tour == 4


def test_vaisseau_leger_avance_de_2_cases_en_4_tours():
    """Le vaisseau léger va vers la gauche, à la vitesse c/2."""
    jeu = jeu_avec(MOTIFS["Vaisseau léger"], 10, 3, largeur=20, hauteur=10)
    depart = cases_vivantes(jeu)
    for _ in range(4):
        jeu.tour_suivant()
    assert cases_vivantes(jeu) == {(x - 2, y) for x, y in depart}


def test_population_des_motifs():
    jeu = jeu_avec(MOTIFS["Pulsar"], 0, 0, largeur=15, hauteur=15)
    assert jeu.population() == 48
    assert jeu_avec(MOTIFS["Canon de Gosper"], 0, 0, 40, 12).population() == 36
    jeu.vider()
    assert jeu.population() == 0 and jeu.tour == 0


def test_canon_de_gosper_produit_des_planeurs():
    jeu = jeu_avec(MOTIFS["Canon de Gosper"], 1, 1, largeur=60, hauteur=40)
    population_initiale = jeu.population()   # 36 cellules
    for _ in range(120):
        jeu.tour_suivant()
    # Période 30 : en 120 tours, le canon a produit 4 planeurs de 5 cellules.
    assert jeu.population() == population_initiale + 4 * 5


def test_pentadecathlon_et_diehard():
    jeu = Jdlv(30, 20, torique=False)
    jeu.charger_motif(MOTIFS["Pentadécathlon"])
    avancer_jusqu_a_stabilisation(jeu)
    assert jeu.statut == CYCLE and jeu.periode == 15

    jeu = Jdlv(40, 40, torique=False)
    jeu.charger_motif(MOTIFS["Diehard"])
    avancer_jusqu_a_stabilisation(jeu)
    assert jeu.statut == EXTINCTION and jeu.tour == 130


# ----------------------------------------------------------------------
# 5. Comparaison avec une implémentation de référence
# ----------------------------------------------------------------------
def tour_suivant_reference(vivantes, largeur, hauteur, torique):
    """Calcul indépendant du tour suivant, sans objets : on compte, pour
    chaque case, combien de cellules vivantes l'entourent."""
    compte = {}
    for (x, y) in vivantes:
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                vx, vy = x + dx, y + dy
                if torique:
                    vx, vy = vx % largeur, vy % hauteur
                elif not (0 <= vx < largeur and 0 <= vy < hauteur):
                    continue
                compte[(vx, vy)] = compte.get((vx, vy), 0) + 1
    return {case for case, n in compte.items()
            if n == 3 or (n == 2 and case in vivantes)}


def test_comparaison_avec_une_implementation_de_reference():
    """Sur des tableaux aléatoires, les deux calculs doivent toujours être
    d'accord. Ce test détecterait par exemple une mise à jour « en une seule
    étape » (cellules modifiées pendant le parcours)."""
    random.seed(2026)
    for torique in (True, False):
        jeu = Jdlv(23, 17, torique)
        jeu.remplir_aleatoirement(0.35)
        attendu = cases_vivantes(jeu)
        for _ in range(60):
            jeu.tour_suivant()
            attendu = tour_suivant_reference(attendu, 23, 17, torique)
            assert cases_vivantes(jeu) == attendu


# ----------------------------------------------------------------------
# 6. Historique et détection des cycles
# ----------------------------------------------------------------------
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


def test_modifier_une_cellule_relance_la_detection():
    jeu = jeu_avec(["OO", "OO"], 4, 4)
    jeu.tour_suivant()
    assert jeu.statut == STABLE
    jeu.modifier_cellule(0, 0, True)
    assert jeu.statut == EN_EVOLUTION and jeu.populations[-1] == 5


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


# ----------------------------------------------------------------------
# 7. Format RLE
# ----------------------------------------------------------------------
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
    doit_echouer(lire_rle, "x = 3, y = 3\nbo$2bo%3o!")


def test_charger_et_extraire_un_motif():
    jeu = Jdlv(20, 20)
    jeu.charger_motif(MOTIFS["Planeur"], "B36/S23")
    assert jeu.motif_actuel() == MOTIFS["Planeur"] and str(jeu.regle) == "B36/S23"
    assert jeu.tour == 0 and jeu.populations == [5]
    doit_echouer(jeu.charger_motif, MOTIFS["Canon de Gosper"])   # 36 colonnes > 20
    assert jeu.motif_actuel() == MOTIFS["Planeur"]               # rien n'a changé


# ----------------------------------------------------------------------
# 8. Affichage console
# ----------------------------------------------------------------------
def test_affichage_console():
    jeu = jeu_avec(MOTIFS["Clignotant"], 3, 4)
    ihm = Jdlv_IHM_Console(jeu, delai=0)
    ihm.effacer_ecran = lambda: None          # on n'efface pas l'écran pendant le test
    with redirect_stdout(io.StringIO()) as sortie:
        ihm.lancer()
    texte = sortie.getvalue()
    assert "■ ■ ■" in texte                     # le clignotant horizontal est affiché
    assert "Tour 2" in texte and "Cycle de période 2" in texte   # arrêt automatique
    assert jeu.tour == 2


# ----------------------------------------------------------------------
# 9. Doctests : les exemples écrits dans les docstrings sont exacts
# ----------------------------------------------------------------------
def test_exemples_des_docstrings():
    import cellule
    import motifs
    import regle
    import rle
    for module in (cellule, motifs, regle, rle):
        echecs, nb_exemples = doctest.testmod(module)
        assert nb_exemples > 0 and echecs == 0, module.__name__


if __name__ == "__main__":
    tests = [f for nom, f in list(globals().items()) if nom.startswith("test_")]
    for test in tests:
        test()
        print("OK  ", test.__name__)
    print(f"\n{len(tests)} tests réussis.")
