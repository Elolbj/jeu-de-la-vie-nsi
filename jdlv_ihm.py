"""
Module jdlv_ihm : interface graphique (Tkinter + Canvas) du jeu de la vie.

La classe Jdlv_IHM affiche un jeu (Jdlv) et permet d'interagir avec lui :
lancer / mettre en pause l'animation, avancer d'un tour, dessiner des
cellules à la souris, placer des motifs célèbres, changer de règle,
régler la vitesse...
"""

import os
import tkinter as tk
from itertools import repeat
from tkinter import filedialog, messagebox, ttk

from jdlv import AGE, EN_EVOLUTION, ETAT
from materiel import Materiel, milliers
from motifs import MOTIFS, dimensions_motif
from regle import REGLES
from rle import ecrire_fichier_rle, lire_fichier_rle

# Dossier proposé par défaut pour ouvrir / enregistrer les motifs
DOSSIER_MOTIFS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "motifs_rle")
TYPES_FICHIERS = [("Motifs RLE", "*.rle"), ("Tous les fichiers", "*.*")]

# Couleurs de l'affichage
COULEUR_FOND = "#1e1e2e"      # cellule morte
COULEUR_LIGNES = "#2a2a3c"    # quadrillage
COULEUR_VIVANTE = "#a6e3a1"   # cellule vivante (quand on n'affiche pas l'âge)
COULEUR_COURBE = "#89b4fa"    # courbe de population
HAUTEUR_COURBE = 80           # hauteur du graphique, en pixels

# En dessous de cette taille de case, on dessine une image (PhotoImage) au lieu
# d'un rectangle par case : Tkinter rame au-delà de quelques dizaines de
# milliers de rectangles.
TAILLE_MIN_RECTANGLES = 5
# La place donnée au tableau et les tailles proposées dépendent de l'écran et
# de la vitesse de la machine : voir materiel.py.

# Couleur d'une cellule vivante selon son âge : (âge maximum, couleur)
COULEURS_AGE = [
    (1, "#f9e2af"),    # vient de naître : jaune
    (2, "#a6e3a1"),    # vert
    (4, "#94e2d5"),    # turquoise
    (9, "#89dceb"),    # bleu ciel
    (19, "#89b4fa"),   # bleu
    (None, "#cba6f7"), # 20 tours et plus : mauve (structures stables)
]

AIDE = """Souris
  Clic + glisser : dessiner (ou effacer si on part d'une cellule vivante)
  Maj + clic : placer le motif choisi

Clavier
  Ctrl+O / Ctrl+S : ouvrir / enregistrer un motif (format RLE)
  Espace : démarrer / pause
  Entrée : tour suivant
  Retour arrière : tour précédent

Statut
  Le jeu retient les états déjà rencontrés. S'il retombe sur l'un d'eux,
  il sait que tout va se répéter : il affiche « stable » ou « cycle de
  période p » et peut mettre l'animation en pause automatiquement.

Règles (notation B/S)
  B = nombres de voisines qui font naître une cellule morte
  S = nombres de voisines qui permettent à une cellule vivante de survivre
  Conway : B3/S23. On peut taper sa propre règle puis appuyer sur Entrée.

Couleurs
  Jaune = cellule qui vient de naître ... mauve = vivante depuis 20 tours ou plus"""


def taille_case_pour(largeur, hauteur, zone):
    """Côté d'une case (en pixels) pour que le tableau tienne dans la zone."""
    largeur_zone, hauteur_zone = zone
    return max(1, min(12, largeur_zone // largeur, hauteur_zone // hauteur))


def couleur_selon_age(age):
    """Renvoie la couleur d'une cellule vivante d'âge donné."""
    for age_max, couleur in COULEURS_AGE:
        if age_max is None or age <= age_max:
            return couleur


# Tables de couleurs calculées une fois pour toutes : âge -> couleur (âge 0 =
# case morte ; au-delà de 19, COULEUR_AGEE) et Etat -> couleur.
COULEUR_PAR_AGE = {age: couleur_selon_age(age) for age in range(1, 20)}
COULEUR_PAR_AGE[0] = COULEUR_FOND
COULEUR_AGEE = COULEURS_AGE[-1][1]
COULEUR_PAR_ETAT = [COULEUR_FOND, COULEUR_VIVANTE]


class Jdlv_IHM:
    """Interface graphique (Tkinter + Canvas) qui affiche et anime un Jdlv."""

    def __init__(self, jeu, taille_cellule=None):
        self.jeu = jeu
        self.en_cours = False         # True quand l'animation tourne
        self.id_minuteur = None       # identifiant renvoyé par after()
        self.mode_dessin = True       # True : on dessine, False : on efface

        self.fenetre = tk.Tk()
        self.fenetre.title("Jeu de la vie de John Horton Conway")
        self.fenetre.resizable(False, False)

        # Matériel : la place du tableau et les tailles proposées en dépendent
        self.materiel = Materiel.detecter()
        self.materiel.definir_ecran(self.fenetre.winfo_screenwidth(),
                                    self.fenetre.winfo_screenheight())
        self.zone = self.materiel.zone_affichage()
        self.tailles = self.materiel.tailles_proposees(self.zone)
        # côté d'une case, en pixels (calculé selon la taille du tableau si absent)
        self.taille = taille_cellule or taille_case_pour(jeu.largeur, jeu.hauteur, self.zone)

        self._creer_menu()
        self._creer_canevas()
        self._creer_courbe()
        self._creer_panneau()
        self._associer_evenements()
        self.dessiner()

    # ------------------------------------------------------------------
    # Construction de l'interface
    # ------------------------------------------------------------------
    def _creer_menu(self):
        """Crée la barre de menus (Fichier, Aide)."""
        barre = tk.Menu(self.fenetre)
        menu_fichier = tk.Menu(barre, tearoff=False)
        menu_fichier.add_command(label="Ouvrir un motif (.rle)...", accelerator="Ctrl+O",
                                 command=self.ouvrir_rle)
        menu_fichier.add_command(label="Enregistrer le tableau (.rle)...",
                                 accelerator="Ctrl+S", command=self.enregistrer_rle)
        menu_fichier.add_separator()
        menu_fichier.add_command(label="Quitter", command=self.fenetre.destroy)
        barre.add_cascade(label="Fichier", menu=menu_fichier)
        menu_aide = tk.Menu(barre, tearoff=False)
        menu_aide.add_command(label="Commandes et règles", command=self.afficher_aide)
        menu_aide.add_command(label="Matériel détecté", command=self.afficher_materiel)
        barre.add_cascade(label="Aide", menu=menu_aide)
        self.fenetre.config(menu=barre)

    def _creer_canevas(self):
        """Crée la zone de dessin.

        Grandes cases : un rectangle par cellule. Petites cases (tableau
        immense) : une image d'un pixel par cellule, agrandie avec zoom().
        """
        largeur_px = self.jeu.largeur * self.taille
        hauteur_px = self.jeu.hauteur * self.taille
        self.canevas = tk.Canvas(self.fenetre, width=largeur_px, height=hauteur_px,
                                 bg=COULEUR_FOND, highlightthickness=0)
        self.canevas.grid(row=0, column=0, padx=10, pady=10, sticky="n")
        self.mode_image = self.taille < TAILLE_MIN_RECTANGLES
        if self.mode_image:
            self.image = tk.PhotoImage(width=self.jeu.largeur, height=self.jeu.hauteur)
            self.image_affichee = self.image
            self.id_image = self.canevas.create_image(0, 0, anchor="nw", image=self.image)
            return

        # On crée les rectangles une seule fois ; ensuite on ne fera que
        # changer leur couleur, ce qui est beaucoup plus rapide.
        self.rectangles = []
        self.couleurs_affichees = []  # couleur actuellement dessinée pour chaque case
        for y in range(self.jeu.hauteur):
            ligne_rect = []
            for x in range(self.jeu.largeur):
                x0 = x * self.taille
                y0 = y * self.taille
                rect = self.canevas.create_rectangle(
                    x0, y0, x0 + self.taille, y0 + self.taille,
                    fill=COULEUR_FOND, outline=COULEUR_LIGNES)
                ligne_rect.append(rect)
            self.rectangles.append(ligne_rect)
            self.couleurs_affichees.append([COULEUR_FOND] * self.jeu.largeur)

    def _creer_courbe(self):
        """Crée, sous le tableau, le graphique de l'évolution de la population."""
        self.courbe = tk.Canvas(self.fenetre, width=self.jeu.largeur * self.taille,
                                height=HAUTEUR_COURBE, bg=COULEUR_FOND,
                                highlightthickness=0)
        self.courbe.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="n")
        # Si le panneau de droite est plus haut que le tableau, l'espace en trop
        # va tout en bas (et pas entre le tableau, la courbe et les statistiques).
        self.fenetre.rowconfigure(3, weight=1)

    def _bouton(self, parent, texte, commande):
        """Crée un bouton qui ne prend pas le focus : sinon la touche Espace
        actionnerait aussi ce bouton, en plus du raccourci clavier."""
        bouton = ttk.Button(parent, text=texte, command=commande, takefocus=False)
        bouton.pack(fill="x", pady=2)
        return bouton

    def _creer_panneau(self):
        """Crée le panneau de commandes à droite du tableau."""
        panneau = ttk.Frame(self.fenetre, padding=(0, 10, 10, 10))
        panneau.grid(row=0, column=1, rowspan=4, sticky="n")

        # --- Animation ---
        cadre = ttk.LabelFrame(panneau, text="Animation", padding=8)
        cadre.pack(fill="x", pady=(0, 8))
        self.bouton_lecture = self._bouton(cadre, "Démarrer", self.basculer_lecture)
        self._bouton(cadre, "Tour suivant", self.etape)
        self._bouton(cadre, "Tour précédent", self.retour_arriere)
        self.vitesse = tk.IntVar(value=10)
        tk.Scale(cadre, from_=1, to=60, orient="horizontal", variable=self.vitesse,
                 label="Vitesse (tours / s)", length=190).pack(fill="x", pady=(4, 0))

        # --- Tableau ---
        cadre = ttk.LabelFrame(panneau, text="Tableau", padding=8)
        cadre.pack(fill="x", pady=(0, 8))
        self.taille_choisie = tk.StringVar(value=self._nom_taille())
        liste_tailles = ttk.Combobox(cadre, textvariable=self.taille_choisie,
                                     values=list(self.tailles.keys()), state="readonly")
        liste_tailles.pack(fill="x", pady=2)
        liste_tailles.bind("<<ComboboxSelected>>", self.choisir_taille)
        ligne = ttk.Frame(cadre)
        ligne.pack(fill="x", pady=2)
        self.largeur_voulue = tk.IntVar(value=self.jeu.largeur)
        self.hauteur_voulue = tk.IntVar(value=self.jeu.hauteur)
        ttk.Spinbox(ligne, from_=3, to=self.zone[0], width=5,
                    textvariable=self.largeur_voulue).pack(side="left")
        ttk.Label(ligne, text=" × ").pack(side="left")
        ttk.Spinbox(ligne, from_=3, to=self.zone[1], width=5,
                    textvariable=self.hauteur_voulue).pack(side="left")
        ttk.Button(ligne, text="Appliquer", command=self.appliquer_taille,
                   takefocus=False).pack(side="right")
        self.texte_taille = tk.StringVar()
        ttk.Label(cadre, textvariable=self.texte_taille, foreground="#666666").pack(anchor="w")
        self._bouton(cadre, "Remplissage aléatoire", self.remplir_aleatoirement)
        self._bouton(cadre, "Tout effacer", self.effacer)
        self.torique = tk.BooleanVar(value=self.jeu.torique)
        ttk.Checkbutton(cadre, text="Bords reliés (tore)", variable=self.torique,
                        command=self.changer_torique, takefocus=False).pack(anchor="w")

        # --- Règles ---
        cadre = ttk.LabelFrame(panneau, text="Règle (B/S)", padding=8)
        cadre.pack(fill="x", pady=(0, 8))
        self.texte_regle = tk.StringVar(value=self._nom_regle(str(self.jeu.regle)))
        choix = [f"{notation}  {nom}" for nom, notation in REGLES.items()]
        self.liste_regles = ttk.Combobox(cadre, textvariable=self.texte_regle, values=choix)
        self.liste_regles.pack(fill="x", pady=2)
        self.liste_regles.bind("<<ComboboxSelected>>", self.appliquer_regle)
        self.liste_regles.bind("<Return>", self.appliquer_regle)

        self.afficher_age = tk.BooleanVar(value=True)
        ttk.Checkbutton(cadre, text="Couleur selon l'âge", variable=self.afficher_age,
                        command=self.dessiner, takefocus=False).pack(anchor="w", pady=(4, 0))
        legende = tk.Canvas(cadre, width=190, height=14, highlightthickness=0)
        legende.pack(anchor="w", pady=(2, 0))
        for i, (age_max, couleur) in enumerate(COULEURS_AGE):
            legende.create_rectangle(40 + i * 14, 2, 51 + i * 14, 13,
                                     fill=couleur, outline="")
        legende.create_text(0, 8, text="jeune", anchor="w", font=("TkDefaultFont", 8))
        legende.create_text(128, 8, text="ancienne", anchor="w", font=("TkDefaultFont", 8))

        # --- Motifs ---
        cadre = ttk.LabelFrame(panneau, text="Motifs", padding=8)
        cadre.pack(fill="x", pady=(0, 8))
        self.motif_choisi = tk.StringVar(value="Planeur")
        liste = ttk.Combobox(cadre, textvariable=self.motif_choisi,
                             values=list(MOTIFS.keys()), state="readonly")
        liste.pack(fill="x", pady=2)
        # Après un choix, on rend le focus à la fenêtre pour que les raccourcis marchent.
        liste.bind("<<ComboboxSelected>>", lambda evenement: self.fenetre.focus_set())
        self._bouton(cadre, "Placer au centre", self.placer_motif_au_centre)

        # --- Statistiques : une ligne sous la courbe ---
        cadre = ttk.Frame(self.fenetre, padding=(10, 0, 10, 10))
        cadre.grid(row=2, column=0, sticky="ew")
        self.texte_tour = tk.StringVar()
        self.texte_population = tk.StringVar()
        self.texte_statut = tk.StringVar()
        ttk.Label(cadre, textvariable=self.texte_tour, width=14).pack(side="left")
        ttk.Label(cadre, textvariable=self.texte_population, width=20).pack(side="left")
        self.etiquette_statut = ttk.Label(cadre, textvariable=self.texte_statut)
        self.etiquette_statut.pack(side="left")
        self.pause_auto = tk.BooleanVar(value=True)
        ttk.Checkbutton(cadre, text="Pause si stable ou cycle", variable=self.pause_auto,
                        takefocus=False).pack(side="right")

    def _associer_evenements(self):
        """Relie la souris et le clavier aux actions."""
        self._associer_souris()
        self.fenetre.bind("<space>", self._raccourci_lecture)
        self.fenetre.bind("<Return>", self._raccourci_etape)
        self.fenetre.bind("<BackSpace>", self._raccourci_retour)
        self.fenetre.bind("<Control-o>", lambda evenement: self.ouvrir_rle())
        self.fenetre.bind("<Control-s>", lambda evenement: self.enregistrer_rle())

    def _associer_souris(self):
        """Relie les clics sur le tableau aux actions (à refaire si le canevas change)."""
        self.canevas.bind("<Button-1>", self.clic)
        self.canevas.bind("<B1-Motion>", self.glisser)
        self.canevas.bind("<Shift-Button-1>", self.placer_motif_a_la_souris)

    def _saisie_en_cours(self, evenement):
        """True si l'utilisateur est en train de taper dans une zone de texte :
        dans ce cas, Espace et Entrée ne doivent pas piloter l'animation."""
        return isinstance(evenement.widget, (tk.Entry, ttk.Entry))

    def _raccourci_lecture(self, evenement):
        """Touche Espace : démarrer / pause."""
        if not self._saisie_en_cours(evenement):
            self.basculer_lecture()

    def _raccourci_etape(self, evenement):
        """Touche Entrée : tour suivant."""
        if not self._saisie_en_cours(evenement):
            self.etape()

    def _raccourci_retour(self, evenement):
        """Touche Retour arrière : tour précédent."""
        if not self._saisie_en_cours(evenement):
            self.retour_arriere()

    def afficher_aide(self):
        """Ouvre une fenêtre qui résume les commandes et les règles."""
        messagebox.showinfo("Aide", AIDE)

    def afficher_materiel(self):
        """Ouvre une fenêtre qui décrit la machine et les réglages adaptés."""
        messagebox.showinfo("Matériel détecté", self.materiel.description())

    # ------------------------------------------------------------------
    # Affichage
    # ------------------------------------------------------------------
    def couleurs_ligne(self, ligne):
        """Couleurs des cellules d'une ligne du tableau.

        map() avec les tables de couleurs fait tout le travail en C : c'est
        bien plus rapide qu'un appel de fonction Python par cellule.
        """
        if self.afficher_age.get():
            return list(map(COULEUR_PAR_AGE.get, map(AGE, ligne), repeat(COULEUR_AGEE)))
        return list(map(COULEUR_PAR_ETAT.__getitem__, map(ETAT, ligne)))

    def dessiner(self):
        """Met à jour l'écran pour qu'il corresponde au tableau.

        Seules les cases dont la couleur a changé sont redessinées.
        """
        if self.mode_image:
            self._dessiner_image()
        else:
            self._dessiner_rectangles()

        nb_cases = milliers(self.jeu.largeur * self.jeu.hauteur)
        self.texte_taille.set(f"{self.jeu.largeur} × {self.jeu.hauteur} = {nb_cases} cases "
                              f"de {self.taille} px")
        self.texte_tour.set(f"Tour : {self.jeu.tour}")
        self.texte_population.set(f"Population : {self.jeu.population()}")
        self.texte_statut.set(self.jeu.description_statut())
        couleur = "black" if self.jeu.statut == EN_EVOLUTION else "#d20f39"
        self.etiquette_statut.config(foreground=couleur)
        self.dessiner_courbe()

    def _dessiner_rectangles(self):
        """Recolore les rectangles des cases qui ont changé."""
        for y, ligne in enumerate(self.jeu.grille):
            couleurs = self.couleurs_ligne(ligne)
            affichees = self.couleurs_affichees[y]
            if couleurs == affichees:
                continue                     # rien n'a changé sur cette ligne
            for x, couleur in enumerate(couleurs):
                if couleur != affichees[x]:
                    self.canevas.itemconfig(self.rectangles[y][x], fill=couleur)
            self.couleurs_affichees[y] = couleurs

    def _dessiner_image(self):
        """Redessine toute l'image : un pixel par case, puis agrandissement.

        PhotoImage.put() reçoit une ligne de couleurs par rangée du tableau,
        sous la forme "{#rrggbb #rrggbb ...} {...}".
        """
        rangees = ["{" + " ".join(self.couleurs_ligne(ligne)) + "}" for ligne in self.jeu.grille]
        self.image.put(" ".join(rangees))
        if self.taille > 1:
            self.image_affichee = self.image.zoom(self.taille)
            self.canevas.itemconfig(self.id_image, image=self.image_affichee)

    def dessiner_courbe(self):
        """Trace la population des derniers tours (un point tous les 2 pixels)."""
        self.courbe.delete("all")
        largeur = int(self.courbe["width"])
        valeurs = self.jeu.populations[-(largeur // 2):]
        maximum = max(max(valeurs), 1)
        points = []
        for i, valeur in enumerate(valeurs):
            x = i * 2
            y = HAUTEUR_COURBE - 5 - valeur * (HAUTEUR_COURBE - 20) / maximum
            points.extend([x, y])
        if len(points) >= 4:   # il faut au moins deux points pour une ligne
            self.courbe.create_line(points, fill=COULEUR_COURBE, width=2)
        self.courbe.create_text(6, 4, anchor="nw", fill="#cdd6f4",
                                text=f"Population (max affiché : {maximum})",
                                font=("TkDefaultFont", 8))

    # ------------------------------------------------------------------
    # Animation
    # ------------------------------------------------------------------
    def etape(self):
        """Avance d'un tour et rafraîchit l'affichage."""
        self.jeu.tour_suivant()
        self.dessiner()

    def retour_arriere(self):
        """Revient d'un tour en arrière (si l'historique le permet)."""
        self.arreter()
        if self.jeu.tour_precedent():
            self.dessiner()
        else:
            self.fenetre.bell()   # plus d'historique : petit bip

    def basculer_lecture(self):
        """Démarre l'animation si elle est arrêtée, la met en pause sinon."""
        if self.en_cours:
            self.arreter()
        else:
            self.demarrer()

    def demarrer(self):
        """Lance l'animation."""
        self.en_cours = True
        self.bouton_lecture.config(text="Pause")
        self._boucle()

    def arreter(self):
        """Met l'animation en pause et annule le prochain tour programmé."""
        self.en_cours = False
        self.bouton_lecture.config(text="Démarrer")
        if self.id_minuteur is not None:
            self.fenetre.after_cancel(self.id_minuteur)
            self.id_minuteur = None

    def _boucle(self):
        """Calcule un tour puis se reprogramme elle-même avec after().

        On n'utilise pas de boucle while : elle bloquerait la fenêtre, qui ne
        pourrait plus réagir aux clics. after() rend la main à Tkinter entre
        deux tours.
        """
        self.etape()
        if self.pause_auto.get() and self.jeu.statut != EN_EVOLUTION:
            self.arreter()
            return
        delai_ms = 1000 // self.vitesse.get()
        self.id_minuteur = self.fenetre.after(delai_ms, self._boucle)

    # ------------------------------------------------------------------
    # Actions sur le tableau
    # ------------------------------------------------------------------
    def remplir_aleatoirement(self):
        """Bouton « Remplissage aléatoire » : 25 % de cellules vivantes."""
        self.jeu.remplir_aleatoirement(0.25)
        self.dessiner()

    def effacer(self):
        """Bouton « Tout effacer » : vide le tableau et revient au tour 0."""
        self.arreter()
        self.jeu.vider()
        self.dessiner()

    def _nom_taille(self):
        """Nom de la taille actuelle dans la liste TAILLES (ou texte vide)."""
        for nom, dimensions in self.tailles.items():
            if dimensions == (self.jeu.largeur, self.jeu.hauteur):
                return nom
        return ""

    def choisir_taille(self, evenement=None):
        """Liste « Taille » : applique la taille choisie."""
        largeur, hauteur = self.tailles[self.taille_choisie.get()]
        self.largeur_voulue.set(largeur)
        self.hauteur_voulue.set(hauteur)
        self.fenetre.focus_set()
        self.appliquer_taille()

    def appliquer_taille(self):
        """Change la taille du tableau en gardant les cellules vivantes (centrées)."""
        try:
            largeur = int(self.largeur_voulue.get())
            hauteur = int(self.hauteur_voulue.get())
        except (tk.TclError, ValueError):
            messagebox.showerror("Taille invalide", "Largeur et hauteur doivent être des nombres entiers.")
            return
        largeur_max, hauteur_max = self.zone        # au moins un pixel par case
        if not (3 <= largeur <= largeur_max and 3 <= hauteur <= hauteur_max):
            messagebox.showerror("Taille invalide",
                                 f"Largeur entre 3 et {largeur_max}, hauteur entre 3 et {hauteur_max}.")
            return
        if largeur * hauteur > self.materiel.nb_cases_max() and not messagebox.askokcancel(
                "Tableau très grand",
                f"{milliers(largeur * hauteur)} cases, c'est beaucoup pour cette machine "
                f"(environ {self.materiel.tours_par_seconde(largeur * hauteur, taille_case_pour(largeur, hauteur, self.zone))} tour(s) par "
                "seconde au début). Continuer ?"):
            return
        self.arreter()
        self.fenetre.config(cursor="watch")
        self.fenetre.update_idletasks()
        self.jeu = self.jeu.redimensionner(largeur, hauteur)
        self.taille = taille_case_pour(largeur, hauteur, self.zone)
        self.canevas.destroy()
        self.courbe.destroy()
        self._creer_canevas()
        self._creer_courbe()
        self._associer_souris()
        self.taille_choisie.set(self._nom_taille())
        self.fenetre.config(cursor="")
        self.dessiner()

    def changer_torique(self):
        """Case « Bords reliés » : active ou désactive le tore."""
        self.jeu.changer_torique(self.torique.get())

    def _nom_regle(self, notation):
        """Exemple : "B36/S23" devient "B36/S23  HighLife" (nom ajouté si connu)."""
        for nom, regle in REGLES.items():
            if regle == notation:
                return f"{notation}  {nom}"
        return notation

    def appliquer_regle(self, evenement=None):
        """Lit la règle choisie ou tapée (ex. "B36/S23") et l'applique au jeu."""
        texte = self.texte_regle.get().split()
        try:
            self.jeu.changer_regle(texte[0] if texte else "")
        except ValueError as erreur:
            messagebox.showerror("Règle invalide", str(erreur))
        self.texte_regle.set(self._nom_regle(str(self.jeu.regle)))
        self.fenetre.focus_set()
        return "break"  # la touche Entrée ne doit pas aussi faire avancer d'un tour

    def ouvrir_rle(self):
        """Demande un fichier .rle, puis l'affiche au centre d'un tableau vide."""
        self.arreter()
        chemin = filedialog.askopenfilename(title="Ouvrir un motif",
                                            initialdir=DOSSIER_MOTIFS,
                                            filetypes=TYPES_FICHIERS)
        if not chemin:
            return                                   # l'utilisateur a annulé
        try:
            motif, regle = lire_fichier_rle(chemin)
            self.jeu.charger_motif(motif, regle)
        except (OSError, ValueError) as erreur:
            messagebox.showerror("Impossible d'ouvrir ce motif", str(erreur))
            return
        self.texte_regle.set(self._nom_regle(str(self.jeu.regle)))
        self.dessiner()

    def enregistrer_rle(self):
        """Enregistre les cellules vivantes dans un fichier .rle."""
        self.arreter()
        motif = self.jeu.motif_actuel()
        if not motif:
            messagebox.showinfo("Rien à enregistrer", "Le tableau est vide.")
            return
        chemin = filedialog.asksaveasfilename(title="Enregistrer le motif",
                                              initialdir=DOSSIER_MOTIFS,
                                              defaultextension=".rle",
                                              filetypes=TYPES_FICHIERS)
        if not chemin:
            return
        nom = os.path.splitext(os.path.basename(chemin))[0]
        try:
            ecrire_fichier_rle(chemin, motif, str(self.jeu.regle), nom)
        except OSError as erreur:
            messagebox.showerror("Impossible d'enregistrer", str(erreur))

    def placer_motif(self, x, y):
        """Place le motif choisi centré sur la case (x, y)."""
        motif = MOTIFS[self.motif_choisi.get()]
        largeur, hauteur = dimensions_motif(motif)
        self.jeu.placer_motif(motif, x - largeur // 2, y - hauteur // 2)
        self.dessiner()

    def placer_motif_au_centre(self):
        """Bouton « Placer au centre » : place le motif choisi au milieu."""
        self.placer_motif(self.jeu.largeur // 2, self.jeu.hauteur // 2)

    # ------------------------------------------------------------------
    # Souris
    # ------------------------------------------------------------------
    def _case_sous_souris(self, evenement):
        """Convertit la position de la souris (pixels) en case (x, y)."""
        return evenement.x // self.taille, evenement.y // self.taille

    def clic(self, evenement):
        """Au clic, on inverse la case. Le glisser qui suit continuera dans le
        même sens : dessiner si la case était morte, effacer si elle était vivante."""
        x, y = self._case_sous_souris(evenement)
        if self.jeu.est_dans_grille(x, y):
            cellule = self.jeu.get_cellule(x, y)
            self.mode_dessin = not cellule.est_vivante()
            self._peindre(x, y)

    def glisser(self, evenement):
        """Souris déplacée bouton enfoncé : continue de dessiner (ou d'effacer)."""
        x, y = self._case_sous_souris(evenement)
        if self.jeu.est_dans_grille(x, y):
            self._peindre(x, y)

    def _peindre(self, x, y):
        """Rend la case (x, y) vivante ou morte selon le mode de dessin."""
        self.jeu.modifier_cellule(x, y, self.mode_dessin)
        self.dessiner()

    def placer_motif_a_la_souris(self, evenement):
        """Maj + clic : place le motif choisi sous la souris."""
        x, y = self._case_sous_souris(evenement)
        if self.jeu.est_dans_grille(x, y):
            self.placer_motif(x, y)

    # ------------------------------------------------------------------
    def lancer(self):
        """Ouvre la fenêtre et lance la boucle d'événements de Tkinter."""
        self.fenetre.mainloop()
