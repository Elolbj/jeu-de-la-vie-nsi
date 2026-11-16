"""
Module materiel : détecte la machine sur laquelle le jeu est lancé et en
déduit des réglages adaptés (tailles de tableau proposées, taille de
l'affichage, mémoire donnée à l'historique).

On mesure :
  - le système, le processeur, le nombre de cœurs, la mémoire vive ;
  - la taille de l'écran (donnée par Tkinter) ;
  - la vitesse réelle de NOTRE programme : on fait tourner un petit jeu
    pendant un instant et on compte les cellules calculées par seconde.
    C'est la mesure la plus fiable : elle dépend du processeur, mais aussi
    de la version de Python.
"""

import os
import platform
import time

# Profils de machine, du plus modeste au plus puissant
ECONOME = "économe"
EQUILIBRE = "équilibré"
PUISSANT = "puissant"


def milliers(nombre):
    """12345 -> '12 345' (séparateur de milliers à la française)."""
    return f"{int(nombre):,}".replace(",", " ")


def memoire_vive_go():
    """Renvoie la mémoire vive totale en Go, ou None si on ne sait pas la lire."""
    try:                                    # Linux et macOS
        return os.sysconf("SC_PAGE_SIZE") * os.sysconf("SC_PHYS_PAGES") / 1e9
    except (AttributeError, ValueError, OSError):
        pass
    if platform.system() == "Windows":
        try:
            import ctypes

            class EtatMemoire(ctypes.Structure):
                """Structure MEMORYSTATUSEX de Windows."""
                _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                            ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong),
                            ("ullTotalPageFile", ctypes.c_ulonglong), ("ullAvailPageFile", ctypes.c_ulonglong),
                            ("ullTotalVirtual", ctypes.c_ulonglong), ("ullAvailVirtual", ctypes.c_ulonglong),
                            ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]

            etat = EtatMemoire()
            etat.dwLength = ctypes.sizeof(etat)
            ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(etat))
            return etat.ullTotalPhys / 1e9
        except (OSError, AttributeError):
            pass
    return None


class Materiel:
    """Caractéristiques de la machine et réglages qui en découlent."""

    _instance = None        # la détection n'est faite qu'une fois (voir detecter)

    # Mémoire prise par une cellule Python (objet + liste de 8 voisines), en octets
    OCTETS_PAR_CELLULE = 250
    # Le dessin coûte plus cher que le calcul : par case, environ 8 fois le
    # temps de calcul avec un rectangle Tkinter par case, 2,5 fois avec une
    # image (mesures faites sur ce projet).
    COUT_DESSIN_RECTANGLES = 8
    COUT_DESSIN_IMAGE = 2.5
    # Taille d'une case à l'écran pour chaque taille de tableau proposée
    TAILLES_DE_CASE = [(12, "Normal"), (7, "Grand"), (4, "Très grand"),
                       (2, "Immense"), (1, "Gigantesque")]

    def __init__(self):
        self.systeme = platform.system() or "inconnu"      # Windows, Linux, Darwin (macOS)
        self.processeur = platform.machine() or "inconnu"   # x86_64, arm64...
        self.nb_coeurs = os.cpu_count() or 1
        self.memoire_go = memoire_vive_go()
        self.version_python = platform.python_version()
        self.largeur_ecran = None
        self.hauteur_ecran = None
        self.cellules_par_seconde = None

    @classmethod
    def detecter(cls):
        """Renvoie le matériel détecté (mesuré une seule fois, puis réutilisé)."""
        if cls._instance is None:
            cls._instance = Materiel()
            cls._instance.mesurer_vitesse()
            cls._instance.lire_ecran()
        return cls._instance

    def lire_ecran(self):
        """Lit la taille de l'écran avec une fenêtre Tkinter invisible
        (rien n'est lu s'il n'y a pas d'écran ou pas de Tkinter)."""
        try:
            import tkinter
            racine = tkinter.Tk()
            racine.withdraw()
            self.definir_ecran(racine.winfo_screenwidth(), racine.winfo_screenheight())
            racine.destroy()
        except Exception:                   # pas d'écran (serveur), pas de Tkinter...
            pass

    # ------------------------------------------------------------------
    # Mesures
    # ------------------------------------------------------------------
    def mesurer_vitesse(self, duree=0.25):
        """Fait tourner un tableau de 60 x 60 cases rempli au hasard pendant
        environ `duree` secondes, et renvoie le nombre de cellules calculées
        par seconde (début de partie : presque toutes les cases changent)."""
        from jdlv import Jdlv               # import ici : jdlv n'a pas besoin de ce module

        jeu = Jdlv(60, 60, torique=True)
        jeu.remplir_aleatoirement(0.3)
        tours = 0
        debut = time.perf_counter()
        while tours < 3 or (time.perf_counter() - debut < duree and tours < 30):
            jeu.tour_suivant()
            tours += 1
        self.cellules_par_seconde = 60 * 60 * tours / (time.perf_counter() - debut)
        return self.cellules_par_seconde

    def definir_ecran(self, largeur, hauteur):
        """Enregistre la taille de l'écran (en pixels), lue par Tkinter."""
        self.largeur_ecran = largeur
        self.hauteur_ecran = hauteur

    # ------------------------------------------------------------------
    # Réglages déduits
    # ------------------------------------------------------------------
    def profil(self):
        """Économe, équilibré ou puissant, selon la vitesse mesurée et la mémoire."""
        vitesse = self.cellules_par_seconde or 0
        memoire = self.memoire_go if self.memoire_go is not None else 4
        if vitesse >= 1_000_000 and memoire >= 8:
            return PUISSANT
        if vitesse >= 300_000 and memoire >= 3:
            return EQUILIBRE
        return ECONOME

    def nb_cases_max(self):
        """Plus grand tableau raisonnable : au moins 2 tours par seconde en
        début de partie (calcul + dessin d'une image), et pas plus de 10 % de
        la mémoire vive pour les cellules."""
        par_vitesse = (self.cellules_par_seconde or 200_000) / (2 * (1 + self.COUT_DESSIN_IMAGE))
        memoire = self.memoire_go if self.memoire_go is not None else 4
        par_memoire = memoire * 1e9 * 0.10 / self.OCTETS_PAR_CELLULE
        return int(min(par_vitesse, par_memoire))

    def zone_affichage(self):
        """Place (en pixels) donnée au tableau dans la fenêtre : environ 60 %
        de l'écran, entre 640 x 420 et 1 400 x 900."""
        if self.largeur_ecran is None:
            return 880, 560
        largeur = max(640, min(1400, int(self.largeur_ecran * 0.60)))
        hauteur = max(420, min(900, int(self.hauteur_ecran * 0.62)))
        return largeur, hauteur

    def tailles_proposees(self, zone=None):
        """Tailles de tableau adaptées à l'écran et à la vitesse de la machine.

        Renvoie un dictionnaire {nom affiché: (largeur, hauteur)}. Chaque taille
        remplit la zone d'affichage avec des cases de 12, 7, 4, 2 ou 1 pixels ;
        celles qui seraient trop lentes ou trop gourmandes ne sont pas proposées.
        """
        largeur_zone, hauteur_zone = zone or self.zone_affichage()
        tailles = {}
        for taille_case, nom in self.TAILLES_DE_CASE:
            largeur = largeur_zone // taille_case
            hauteur = hauteur_zone // taille_case
            if largeur * hauteur > self.nb_cases_max() and tailles:
                break
            tours = self.tours_par_seconde(largeur * hauteur, taille_case)
            vitesse = f"{tours:g}".replace(".", ",")
            tailles[f"{nom} {largeur}×{hauteur} · ≈{vitesse} t/s"] = (largeur, hauteur)
        return tailles

    def tours_par_seconde(self, nb_cases, taille_case=2):
        """Estimation du nombre de tours par seconde en début de partie,
        dessin compris (rectangles si les cases font 5 pixels ou plus)."""
        cout_dessin = self.COUT_DESSIN_RECTANGLES if taille_case >= 5 else self.COUT_DESSIN_IMAGE
        tours = (self.cellules_par_seconde or 200_000) / (nb_cases * (1 + cout_dessin))
        return round(tours) if tours >= 10 else round(tours, 1)

    def taille_de_depart(self):
        """Taille du tableau au lancement : plus grande sur une machine rapide."""
        largeur_zone, hauteur_zone = self.zone_affichage()
        taille_case = 12 if self.profil() == ECONOME else 7
        return max(40, largeur_zone // taille_case), max(26, hauteur_zone // taille_case)

    def budget_historique(self):
        """Mémoire donnée au retour arrière : 2 % de la mémoire vive,
        entre 16 Mo et 256 Mo (64 Mo si la mémoire est inconnue)."""
        if self.memoire_go is None:
            return 64_000_000
        return int(max(16e6, min(256e6, self.memoire_go * 1e9 * 0.02)))

    def description(self):
        """Résumé lisible du matériel et des réglages choisis."""
        memoire = (f"{self.memoire_go:.1f} Go".replace(".", ",")
                   if self.memoire_go is not None else "inconnue")
        ecran = (f"{self.largeur_ecran} × {self.hauteur_ecran} px"
                 if self.largeur_ecran else "inconnu")
        vitesse = (f"{self.cellules_par_seconde / 1e6:.2f}".replace(".", ",")
                   if self.cellules_par_seconde else "?")
        largeur_zone, hauteur_zone = self.zone_affichage()
        return (f"Système : {self.systeme} ({self.processeur}), Python {self.version_python}\n"
                f"Processeur : {self.nb_coeurs} cœur(s)\n"
                f"Mémoire vive : {memoire}\n"
                f"Écran : {ecran}\n"
                f"Vitesse mesurée : {vitesse} million(s) de cellules par seconde\n"
                f"Profil : {self.profil()}\n\n"
                f"Réglages adaptés :\n"
                f"  zone d'affichage : {largeur_zone} × {hauteur_zone} px\n"
                f"  plus grand tableau : {milliers(self.nb_cases_max())} cases\n"
                f"  mémoire du retour arrière : {self.budget_historique() // 1_000_000} Mo")
