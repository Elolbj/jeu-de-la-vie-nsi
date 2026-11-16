"""
Module jdlv_ihm : interface graphique (Tkinter + Canvas) du jeu de la vie.

La classe Jdlv_IHM affiche un jeu (Jdlv) et permet d'interagir avec lui :
lancer / mettre en pause l'animation, avancer d'un tour, dessiner des
cellules à la souris, placer des motifs célèbres, changer de règle,
régler la vitesse...
"""

import tkinter as tk
from tkinter import messagebox, ttk

from jdlv import EN_EVOLUTION
from motifs import MOTIFS, dimensions_motif
from regle import REGLES

# Couleurs de l'affichage
COULEUR_FOND = "#1e1e2e"      # cellule morte
COULEUR_LIGNES = "#2a2a3c"    # quadrillage
COULEUR_VIVANTE = "#a6e3a1"   # cellule vivante (quand on n'affiche pas l'âge)
COULEUR_COURBE = "#89b4fa"    # courbe de population
HAUTEUR_COURBE = 80           # hauteur du graphique, en pixels

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


def couleur_selon_age(age):
    """Renvoie la couleur d'une cellule vivante d'âge donné."""
    for age_max, couleur in COULEURS_AGE:
        if age_max is None or age <= age_max:
            return couleur


class Jdlv_IHM:
    """Interface graphique (Tkinter + Canvas) qui affiche et anime un Jdlv."""

    def __init__(self, jeu, taille_cellule=12):
        self.jeu = jeu
        self.taille = taille_cellule  # côté d'une case, en pixels
        self.en_cours = False         # True quand l'animation tourne
        self.id_minuteur = None       # identifiant renvoyé par after()
        self.mode_dessin = True       # True : on dessine, False : on efface

        self.fenetre = tk.Tk()
        self.fenetre.title("Jeu de la vie de John Horton Conway")
        self.fenetre.resizable(False, False)

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
        barre = tk.Menu(self.fenetre)
        menu_aide = tk.Menu(barre, tearoff=False)
        menu_aide.add_command(label="Commandes et règles", command=self.afficher_aide)
        barre.add_cascade(label="Aide", menu=menu_aide)
        self.fenetre.config(menu=barre)

    def _creer_canevas(self):
        """Crée la zone de dessin et un rectangle par cellule."""
        largeur_px = self.jeu.largeur * self.taille
        hauteur_px = self.jeu.hauteur * self.taille
        self.canevas = tk.Canvas(self.fenetre, width=largeur_px, height=hauteur_px,
                                 bg=COULEUR_FOND, highlightthickness=0)
        self.canevas.grid(row=0, column=0, padx=10, pady=10, sticky="n")

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

    def _bouton(self, parent, texte, commande):
        """Crée un bouton qui ne prend pas le focus : sinon la touche Espace
        actionnerait aussi ce bouton, en plus du raccourci clavier."""
        bouton = ttk.Button(parent, text=texte, command=commande, takefocus=False)
        bouton.pack(fill="x", pady=2)
        return bouton

    def _creer_panneau(self):
        """Crée le panneau de commandes à droite du tableau."""
        panneau = ttk.Frame(self.fenetre, padding=(0, 10, 10, 10))
        panneau.grid(row=0, column=1, rowspan=2, sticky="n")

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

        # --- Statistiques ---
        cadre = ttk.LabelFrame(panneau, text="Statistiques", padding=8)
        cadre.pack(fill="x")
        self.texte_tour = tk.StringVar()
        self.texte_population = tk.StringVar()
        self.texte_statut = tk.StringVar()
        ttk.Label(cadre, textvariable=self.texte_tour).pack(anchor="w")
        ttk.Label(cadre, textvariable=self.texte_population).pack(anchor="w")
        self.etiquette_statut = ttk.Label(cadre, textvariable=self.texte_statut)
        self.etiquette_statut.pack(anchor="w")
        self.pause_auto = tk.BooleanVar(value=True)
        ttk.Checkbutton(cadre, text="Pause si stable ou cycle", variable=self.pause_auto,
                        takefocus=False).pack(anchor="w", pady=(4, 0))

    def _associer_evenements(self):
        """Relie la souris et le clavier aux actions."""
        self.canevas.bind("<Button-1>", self.clic)
        self.canevas.bind("<B1-Motion>", self.glisser)
        self.canevas.bind("<Shift-Button-1>", self.placer_motif_a_la_souris)
        self.fenetre.bind("<space>", self._raccourci_lecture)
        self.fenetre.bind("<Return>", self._raccourci_etape)
        self.fenetre.bind("<BackSpace>", self._raccourci_retour)

    def _saisie_en_cours(self, evenement):
        """True si l'utilisateur est en train de taper dans une zone de texte :
        dans ce cas, Espace et Entrée ne doivent pas piloter l'animation."""
        return isinstance(evenement.widget, (tk.Entry, ttk.Entry))

    def _raccourci_lecture(self, evenement):
        if not self._saisie_en_cours(evenement):
            self.basculer_lecture()

    def _raccourci_etape(self, evenement):
        if not self._saisie_en_cours(evenement):
            self.etape()

    def _raccourci_retour(self, evenement):
        if not self._saisie_en_cours(evenement):
            self.retour_arriere()

    def afficher_aide(self):
        messagebox.showinfo("Aide", AIDE)

    # ------------------------------------------------------------------
    # Affichage
    # ------------------------------------------------------------------
    def couleur_cellule(self, cellule):
        if not cellule.est_vivante():
            return COULEUR_FOND
        if self.afficher_age.get():
            return couleur_selon_age(cellule.age)
        return COULEUR_VIVANTE

    def dessiner(self):
        """Met à jour l'écran pour qu'il corresponde au tableau.

        Seules les cases dont la couleur a changé sont redessinées.
        """
        for y in range(self.jeu.hauteur):
            for x in range(self.jeu.largeur):
                couleur = self.couleur_cellule(self.jeu.get_cellule(x, y))
                if couleur != self.couleurs_affichees[y][x]:
                    self.canevas.itemconfig(self.rectangles[y][x], fill=couleur)
                    self.couleurs_affichees[y][x] = couleur

        self.texte_tour.set(f"Tour : {self.jeu.tour}")
        self.texte_population.set(f"Population : {self.jeu.population()}")
        self.texte_statut.set(self.jeu.description_statut())
        couleur = "black" if self.jeu.statut == EN_EVOLUTION else "#d20f39"
        self.etiquette_statut.config(foreground=couleur)
        self.dessiner_courbe()

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
        self.en_cours = True
        self.bouton_lecture.config(text="Pause")
        self._boucle()

    def arreter(self):
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
        self.jeu.remplir_aleatoirement(0.25)
        self.dessiner()

    def effacer(self):
        self.arreter()
        self.jeu.vider()
        self.dessiner()

    def changer_torique(self):
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

    def placer_motif(self, x, y):
        """Place le motif choisi centré sur la case (x, y)."""
        motif = MOTIFS[self.motif_choisi.get()]
        largeur, hauteur = dimensions_motif(motif)
        self.jeu.placer_motif(motif, x - largeur // 2, y - hauteur // 2)
        self.dessiner()

    def placer_motif_au_centre(self):
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
        x, y = self._case_sous_souris(evenement)
        if self.jeu.est_dans_grille(x, y):
            self._peindre(x, y)

    def _peindre(self, x, y):
        self.jeu.modifier_cellule(x, y, self.mode_dessin)
        self.dessiner()

    def placer_motif_a_la_souris(self, evenement):
        x, y = self._case_sous_souris(evenement)
        if self.jeu.est_dans_grille(x, y):
            self.placer_motif(x, y)

    # ------------------------------------------------------------------
    def lancer(self):
        """Ouvre la fenêtre et lance la boucle d'événements de Tkinter."""
        self.fenetre.mainloop()
