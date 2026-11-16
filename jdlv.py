"""
Module jdlv : définit la classe Jdlv, qui représente le jeu de la vie.

Un jeu contient un tableau à deux dimensions (liste de listes) de Cellule
et un compteur de tours. On crée un jeu en instanciant la classe, puis on
le lance avec la méthode start() :

    jeu = Jdlv(70, 50)
    jeu.remplir_aleatoirement()
    jeu.start()
"""

import hashlib
import random
from array import array
from operator import attrgetter

from cellule import Cellule
from motifs import coordonnees_motif, dimensions_motif
from regle import Regle

# attrgetter("Etat")(cellule) vaut cellule.Etat. Avec map(), Python parcourt
# toutes les cellules en C, bien plus vite qu'une boucle for.
ETAT = attrgetter("Etat")
AGE = attrgetter("age")

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

    TAILLE_HISTORIQUE = 500     # nombre maximal de tours que l'on peut annuler
    # Mémoire réservée à l'historique (en octets). main.py l'adapte à la
    # mémoire de l'ordinateur (voir materiel.py). Une photo prend 4 octets par
    # case : pour un très grand tableau, on garde donc moins de tours.
    BUDGET_HISTORIQUE = 64_000_000
    # Nombre d'états retenus pour détecter les cycles. Un cycle plus long n'est
    # pas détecté. Exemple : sur un tore de 70 x 45, un planeur seul revient à
    # sa position de départ après 4 x ppcm(70, 45) = 2520 tours.
    # On ne garde pas les états eux-mêmes (123 200 octets chacun pour 440 x 280,
    # soit 370 Mo pour 3 000 états) mais leur empreinte de 16 octets.
    TAILLE_MEMOIRE = 3000

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

        nb_cases = largeur * hauteur
        self.taille_historique = max(20, min(self.TAILLE_HISTORIQUE,
                                             self.BUDGET_HISTORIQUE // (4 * nb_cases)))
        self._a_recalculer = None   # cellules à recalculer au prochain tour (None = toutes)
        self._vivantes = set()      # cellules vivantes (tenu à jour par tour_suivant)
        self._signature = None      # signature de l'état actuel, calculée une seule fois
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
        """Renvoie le nombre de cellules vivantes (somme des Etat, qui valent 0 ou 1)."""
        return sum(map(ETAT, self._toutes_les_cellules))

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
        self._a_recalculer = None
        self._signature = None

    def _apres_modification(self):
        """À appeler quand le tableau ou la règle change en dehors d'un tour :
        les états déjà vus ne correspondent plus à la même évolution, et il
        faudra recalculer toutes les cellules au prochain tour."""
        self._a_recalculer = None
        self._signature = None
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

    def charger_motif(self, motif, regle=None):
        """Vide le tableau, place le motif au centre et repart du tour 0.

        Si regle est donnée (ex. lue dans un fichier RLE), elle remplace la
        règle actuelle. Lève ValueError si la règle est invalide ou si le
        motif ne tient pas dans le tableau (rien n'est alors modifié).
        """
        nouvelle_regle = Regle(regle) if regle else self.regle
        largeur, hauteur = dimensions_motif(motif) if motif else (0, 0)
        if largeur > self.largeur or hauteur > self.hauteur:
            raise ValueError(f"motif trop grand ({largeur}x{hauteur}) pour un "
                             f"tableau de {self.largeur}x{self.hauteur}")
        self.regle = nouvelle_regle
        self.vider()
        self.placer_motif(motif, (self.largeur - largeur) // 2,
                          (self.hauteur - hauteur) // 2)
        self._remettre_a_zero()

    def redimensionner(self, largeur, hauteur):
        """Renvoie un nouveau jeu de largeur x hauteur cases qui contient les
        cellules vivantes de celui-ci, centrées (celles qui dépassent d'un
        tableau plus petit sont perdues). Le nouveau jeu repart du tour 0."""
        nouveau = Jdlv(largeur, hauteur, self.torique, str(self.regle))
        dx = (largeur - self.largeur) // 2
        dy = (hauteur - self.hauteur) // 2
        for y in range(self.hauteur):
            for x in range(self.largeur):
                ancienne = self.grille[y][x]
                if ancienne.est_vivante() and nouveau.est_dans_grille(x + dx, y + dy):
                    cellule = nouveau.grille[y + dy][x + dx]
                    cellule.naitre()
                    cellule.age = ancienne.age
        nouveau._remettre_a_zero()
        return nouveau

    def motif_actuel(self):
        """Renvoie les cellules vivantes sous forme de motif (liste de chaînes),
        réduit au plus petit rectangle qui les contient ([] si tout est mort)."""
        xs = [x for y in range(self.hauteur) for x in range(self.largeur)
              if self.grille[y][x].est_vivante()]
        ys = [y for y in range(self.hauteur) for x in range(self.largeur)
              if self.grille[y][x].est_vivante()]
        if not xs:
            return []
        motif = []
        for y in range(min(ys), max(ys) + 1):
            ligne = ""
            for x in range(min(xs), max(xs) + 1):
                ligne += "O" if self.grille[y][x].est_vivante() else "."
            motif.append(ligne)
        return motif

    # ------------------------------------------------------------------
    # Évolution
    # ------------------------------------------------------------------
    def tour_suivant(self):
        """Fait passer tout le tableau au tour suivant.

        On procède en DEUX étapes : d'abord toutes les cellules calculent
        leur futur état, ensuite seulement elles l'appliquent. Si on
        modifiait les cellules au fur et à mesure, les voisines déjà mises
        à jour fausseraient le calcul des suivantes.

        Optimisation : l'état futur d'une cellule ne dépend que d'elle et de
        ses 8 voisines. Si aucune des neuf n'a changé au tour précédent, la
        cellule ne peut pas changer. On ne recalcule donc que les cellules
        « actives » : celles qui viennent de changer et leurs voisines. Après
        quelques centaines de tours, il en reste souvent moins de 20 %.
        """
        self._memoriser_etat_actuel()
        if self._a_recalculer is None:          # après une modification : toutes
            a_recalculer = self._toutes_les_cellules
            immobiles_vivantes = []
        else:
            a_recalculer = self._a_recalculer
            immobiles_vivantes = [c for c in self._vivantes if c not in a_recalculer]

        # Étape 1 : calcul des états futurs
        for cellule in a_recalculer:
            cellule.calculer_etat_suivant(self.regle)
        changees = [c for c in a_recalculer if c.etat_suivant != c.Etat]
        # Étape 2 : application
        for cellule in a_recalculer:
            cellule.passer_a_l_etat_suivant()
        for cellule in immobiles_vivantes:      # vivantes non recalculées : elles vieillissent
            cellule.age += 1
        self.tour += 1

        # Préparation du tour suivant : cellules qui ont changé + leurs voisines
        actives = set(changees)
        for cellule in changees:
            actives.update(cellule.voisines)
        if self._a_recalculer is None:
            self._vivantes = {c for c in self._toutes_les_cellules if c.Etat}
        else:
            for cellule in changees:
                if cellule.Etat:
                    self._vivantes.add(cellule)
                else:
                    self._vivantes.discard(cellule)
        self._a_recalculer = actives
        self._signature = None

        self.populations.append(len(self._vivantes))
        self._analyser()

    def tour_precedent(self):
        """Revient au tour précédent. Renvoie False s'il n'y a plus d'historique."""
        if len(self.historique) == 0:
            return False
        photo = self.historique.pop()
        for cellule, age in zip(self._toutes_les_cellules, photo):
            cellule.age = age
            cellule.Etat = 1 if age > 0 else 0
            cellule.etat_suivant = cellule.Etat
        self.tour -= 1
        if len(self.populations) > 1:
            self.populations.pop()
        self._apres_modification()
        return True

    # ------------------------------------------------------------------
    # Mémoire des états : retour arrière et détection des cycles
    # ------------------------------------------------------------------
    def signature(self):
        """Résume l'état du tableau en une empreinte de 16 octets.

        On écrit d'abord l'état complet (un octet 0 ou 1 par case), puis on
        le passe dans une fonction de hachage (BLAKE2) : deux tableaux
        identiques ont la même empreinte, et deux tableaux différents ont
        une chance sur 2 puissance 128 d'avoir la même (en pratique jamais).
        Elle n'est calculée qu'une fois par tour.
        """
        if self._signature is None:
            etat_complet = bytes(map(ETAT, self._toutes_les_cellules))
            self._signature = hashlib.blake2b(etat_complet, digest_size=16).digest()
        return self._signature

    def _memoriser_etat_actuel(self):
        """Garde une photo de l'état actuel (retour arrière) et sa signature (cycles)."""
        # Photo pour le retour arrière : l'âge suffit (âge 0 = cellule morte).
        # array("I") range un entier par case sur 4 octets.
        self.historique.append(array("I", map(AGE, self._toutes_les_cellules)))
        if len(self.historique) > self.taille_historique:
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
