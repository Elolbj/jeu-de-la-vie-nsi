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
from regle import Regle

# Valeurs possibles de l'attribut statut
EN_EVOLUTION = "en évolution"
EXTINCTION = "extinction"
STABLE = "stable"
CYCLE = "cycle"


class Jdlv:
    """Le jeu de la vie : un tableau fini de cellules et un compteur de tours.

    Si torique vaut True, les bords sont reliés : une cellule du bord droit
    a pour voisines les cellules du bord gauche (et de même haut/bas).
    Le tableau se comporte alors comme la surface d'un donut (un tore).
    """

    TAILLE_HISTORIQUE = 500     # nombre de tours que l'on peut annuler
    TAILLE_MEMOIRE = 2000       # nombre d'états retenus pour détecter les cycles

    def __init__(self, largeur=70, hauteur=50, torique=True, regle="B3/S23"):
        assert largeur >= 3 and hauteur >= 3, "le tableau doit faire au moins 3x3"
        self.largeur = largeur
        self.hauteur = hauteur
        self.torique = torique
        self.regle = Regle(regle)   # règle de naissance / survie (Conway par défaut)
        self.tour = 0
        # self.grille[y][x] : y = numéro de ligne, x = numéro de colonne
        self.grille = [[Cellule() for x in range(largeur)] for y in range(hauteur)]
        # Les mêmes cellules dans une seule liste, pour les parcourir facilement
        self._toutes_les_cellules = [c for ligne in self.grille for c in ligne]
        self._relier_voisines()

        self.historique = []        # photos des tours précédents (retour arrière)
        self.populations = [0]      # population à chaque tour (pour la courbe)
        self.deja_vus = {}          # signature d'un état -> tour où on l'a vu
        self.statut = EN_EVOLUTION  # en évolution, extinction, stable ou cycle
        self.periode = None         # période du cycle quand statut == CYCLE

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
        self._apres_modification()

    def changer_regle(self, notation):
        """Change la règle du jeu (ex. "B36/S23"). Lève ValueError si invalide."""
        self.regle = Regle(notation)
        self._apres_modification()

    # ------------------------------------------------------------------
    # Accès aux cellules
    # ------------------------------------------------------------------
    def est_dans_grille(self, x, y):
        """Renvoie True si (x, y) correspond à une case du tableau."""
        return 0 <= x < self.largeur and 0 <= y < self.hauteur

    def get_cellule(self, x, y):
        """Renvoie la cellule située colonne x, ligne y."""
        return self.grille[y][x]

    def cellules(self):
        """Renvoie la liste de toutes les cellules, ligne par ligne."""
        return self._toutes_les_cellules

    def population(self):
        """Renvoie le nombre de cellules vivantes."""
        total = 0
        for cellule in self.cellules():
            total += cellule.Etat
        return total

    # ------------------------------------------------------------------
    # Configuration initiale et modifications
    # ------------------------------------------------------------------
    def _remettre_a_zero(self):
        """Repart du tour 0 avec la configuration actuelle."""
        self.tour = 0
        self.historique = []
        self.populations = [self.population()]
        self.deja_vus = {}
        self.statut = EN_EVOLUTION
        self.periode = None

    def _apres_modification(self):
        """À appeler quand le tableau ou la règle change en dehors d'un tour :
        les états déjà vus ne correspondent plus à la même évolution."""
        self.deja_vus = {}
        self.statut = EN_EVOLUTION
        self.periode = None
        self.populations[-1] = self.population()

    def vider(self):
        """Tue toutes les cellules et remet le compteur de tours à 0."""
        for cellule in self.cellules():
            cellule.mourir()
        self._remettre_a_zero()

    def remplir_aleatoirement(self, densite=0.25):
        """Configuration aléatoire : chaque cellule a une probabilité
        `densite` d'être vivante."""
        assert 0 <= densite <= 1, "la densité est une probabilité"
        for cellule in self.cellules():
            if random.random() < densite:
                cellule.naitre()
            else:
                cellule.mourir()
        self._remettre_a_zero()

    def modifier_cellule(self, x, y, vivante):
        """Rend la cellule (x, y) vivante (vivante=True) ou morte."""
        cellule = self.get_cellule(x, y)
        if vivante:
            cellule.naitre()
        else:
            cellule.mourir()
        self._apres_modification()

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
        self._apres_modification()

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
        self._memoriser_etat_actuel()

        for cellule in self.cellules():
            cellule.calculer_etat_suivant(self.regle)
        for cellule in self.cellules():
            cellule.passer_a_l_etat_suivant()
        self.tour += 1

        self.populations.append(self.population())
        self._analyser()

    def tour_precedent(self):
        """Revient au tour précédent. Renvoie False s'il n'y a plus d'historique."""
        if len(self.historique) == 0:
            return False
        photo = self.historique.pop()
        for cellule, age in zip(self.cellules(), photo):
            cellule.age = age
            cellule.Etat = 1 if age > 0 else 0
        self.tour -= 1
        if len(self.populations) > 1:
            self.populations.pop()
        self._apres_modification()
        return True

    # ------------------------------------------------------------------
    # Mémoire des états : retour arrière et détection des cycles
    # ------------------------------------------------------------------
    def signature(self):
        """Résume l'état du tableau : une suite d'octets valant 0 ou 1.

        Deux tableaux identiques ont la même signature, qu'on peut utiliser
        comme clé de dictionnaire.
        """
        return bytes(cellule.Etat for cellule in self.cellules())

    def _memoriser_etat_actuel(self):
        # Photo pour le retour arrière : l'âge suffit (âge 0 = cellule morte).
        # Un octet ne dépasse pas 255, d'où le min().
        self.historique.append(bytes(min(c.age, 255) for c in self.cellules()))
        if len(self.historique) > self.TAILLE_HISTORIQUE:
            self.historique.pop(0)

        # Mémoire pour la détection des cycles
        if len(self.deja_vus) > self.TAILLE_MEMOIRE:
            self.deja_vus = {}
        signature = self.signature()
        if signature not in self.deja_vus:
            self.deja_vus[signature] = self.tour

    def _analyser(self):
        """Met à jour statut et periode en comparant l'état actuel aux états
        déjà rencontrés : si on retombe sur un état connu, tout se répète."""
        signature = self.signature()
        if self.populations[-1] == 0:
            self.statut, self.periode = EXTINCTION, None
        elif signature in self.deja_vus:
            self.periode = self.tour - self.deja_vus[signature]
            self.statut = STABLE if self.periode == 1 else CYCLE
        else:
            self.statut, self.periode = EN_EVOLUTION, None

    def description_statut(self):
        """Phrase décrivant le statut, pour l'affichage."""
        if self.statut == EXTINCTION:
            return "Extinction : plus aucune cellule"
        if self.statut == STABLE:
            return "Stable : plus rien ne bouge"
        if self.statut == CYCLE:
            return f"Cycle de période {self.periode}"
        return "En évolution"

    # ------------------------------------------------------------------
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
