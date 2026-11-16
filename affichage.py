"""
Module affichage : fenêtre graphique (Tkinter) du jeu de la vie.

La classe FenetreJeu affiche une Grille et permet d'interagir avec elle :
lancer / mettre en pause l'animation, avancer d'une génération, dessiner
des cellules à la souris, placer des motifs célèbres, régler la vitesse...
"""

import tkinter as tk
from tkinter import ttk

from motifs import MOTIFS, dimensions_motif

# Couleurs de l'affichage
COULEUR_FOND = "#1e1e2e"      # cellule morte
COULEUR_VIVANTE = "#a6e3a1"   # cellule vivante
COULEUR_LIGNES = "#2a2a3c"    # quadrillage


class FenetreJeu:
    """Fenêtre Tkinter qui affiche et anime une Grille."""

    def __init__(self, grille, taille_cellule=12):
        self.grille = grille
        self.taille = taille_cellule  # côté d'une case, en pixels
        self.en_cours = False         # True quand l'animation tourne
        self.id_minuteur = None       # identifiant renvoyé par after()
        self.mode_dessin = True       # True : on dessine, False : on efface

        self.fenetre = tk.Tk()
        self.fenetre.title("Jeu de la vie de John Horton Conway")
        self.fenetre.resizable(False, False)

        self._creer_canevas()
        self._creer_panneau()
        self._associer_evenements()
        self.dessiner()

    # ------------------------------------------------------------------
    # Construction de l'interface
    # ------------------------------------------------------------------
    def _creer_canevas(self):
        """Crée la zone de dessin et un rectangle par cellule."""
        largeur_px = self.grille.largeur * self.taille
        hauteur_px = self.grille.hauteur * self.taille
        self.canevas = tk.Canvas(self.fenetre, width=largeur_px, height=hauteur_px,
                                 bg=COULEUR_FOND, highlightthickness=0)
        self.canevas.grid(row=0, column=0, padx=10, pady=10)

        # On crée les rectangles une seule fois ; ensuite on ne fera que
        # changer leur couleur, ce qui est beaucoup plus rapide.
        self.rectangles = []
        self.etat_affiche = []  # ce qui est actuellement dessiné à l'écran
        for y in range(self.grille.hauteur):
            ligne_rect = []
            for x in range(self.grille.largeur):
                x0 = x * self.taille
                y0 = y * self.taille
                rect = self.canevas.create_rectangle(
                    x0, y0, x0 + self.taille, y0 + self.taille,
                    fill=COULEUR_FOND, outline=COULEUR_LIGNES)
                ligne_rect.append(rect)
            self.rectangles.append(ligne_rect)
            self.etat_affiche.append([False] * self.grille.largeur)

    def _creer_panneau(self):
        """Crée le panneau de commandes à droite de la grille."""
        panneau = ttk.Frame(self.fenetre, padding=10)
        panneau.grid(row=0, column=1, sticky="n")

        # --- Commandes de l'animation ---
        cadre_anim = ttk.LabelFrame(panneau, text="Animation", padding=8)
        cadre_anim.pack(fill="x", pady=(0, 10))

        self.bouton_lecture = ttk.Button(cadre_anim, text="Démarrer",
                                         command=self.basculer_lecture,
                                         takefocus=False)
        self.bouton_lecture.pack(fill="x", pady=2)
        ttk.Button(cadre_anim, text="Génération suivante",
                   command=self.etape, takefocus=False).pack(fill="x", pady=2)

        self.vitesse = tk.IntVar(value=10)
        tk.Scale(cadre_anim, from_=1, to=60, orient="horizontal",
                 variable=self.vitesse, label="Vitesse (générations / s)",
                 length=180).pack(fill="x", pady=(6, 0))

        # --- Grille ---
        cadre_grille = ttk.LabelFrame(panneau, text="Grille", padding=8)
        cadre_grille.pack(fill="x", pady=(0, 10))

        ttk.Button(cadre_grille, text="Remplissage aléatoire",
                   command=self.remplir_aleatoirement, takefocus=False).pack(fill="x", pady=2)
        ttk.Button(cadre_grille, text="Tout effacer",
                   command=self.effacer, takefocus=False).pack(fill="x", pady=2)

        self.torique = tk.BooleanVar(value=self.grille.torique)
        ttk.Checkbutton(cadre_grille, text="Bords reliés (tore)",
                        variable=self.torique,
                        command=self.changer_torique,
                        takefocus=False).pack(anchor="w", pady=(6, 0))

        # --- Motifs ---
        cadre_motifs = ttk.LabelFrame(panneau, text="Motifs", padding=8)
        cadre_motifs.pack(fill="x", pady=(0, 10))

        self.motif_choisi = tk.StringVar(value="Planeur")
        liste = ttk.Combobox(cadre_motifs, textvariable=self.motif_choisi,
                             values=list(MOTIFS.keys()), state="readonly")
        liste.pack(fill="x", pady=2)
        # Après un choix, on rend le focus à la fenêtre pour que les raccourcis marchent.
        liste.bind("<<ComboboxSelected>>", lambda evenement: self.fenetre.focus_set())
        ttk.Button(cadre_motifs, text="Placer au centre",
                   command=self.placer_motif_au_centre, takefocus=False).pack(fill="x", pady=2)

        # --- Statistiques ---
        cadre_stats = ttk.LabelFrame(panneau, text="Statistiques", padding=8)
        cadre_stats.pack(fill="x", pady=(0, 10))

        self.texte_generation = tk.StringVar()
        self.texte_population = tk.StringVar()
        ttk.Label(cadre_stats, textvariable=self.texte_generation).pack(anchor="w")
        ttk.Label(cadre_stats, textvariable=self.texte_population).pack(anchor="w")

        # --- Aide ---
        aide = ("Clic + glisser : dessiner / effacer\n"
                "Maj + clic : placer le motif choisi\n"
                "Espace : démarrer / pause\n"
                "Entrée : génération suivante")
        ttk.Label(panneau, text=aide, justify="left",
                  foreground="#666666").pack(anchor="w")

    def _associer_evenements(self):
        """Relie la souris et le clavier aux actions.

        (Les boutons sont créés avec takefocus=False : sinon, la touche Espace
        actionnerait aussi le bouton qui a le focus, en plus du raccourci.)
        """
        self.canevas.bind("<Button-1>", self.clic)
        self.canevas.bind("<B1-Motion>", self.glisser)
        self.canevas.bind("<Shift-Button-1>", self.placer_motif_a_la_souris)
        self.fenetre.bind("<space>", lambda evenement: self.basculer_lecture())
        self.fenetre.bind("<Return>", lambda evenement: self.etape())

    # ------------------------------------------------------------------
    # Affichage
    # ------------------------------------------------------------------
    def dessiner(self):
        """Met à jour l'écran pour qu'il corresponde à la grille.

        Seules les cases qui ont changé sont redessinées.
        """
        for y in range(self.grille.hauteur):
            for x in range(self.grille.largeur):
                vivante = self.grille.get_cellule(x, y).est_vivante()
                if vivante != self.etat_affiche[y][x]:
                    couleur = COULEUR_VIVANTE if vivante else COULEUR_FOND
                    self.canevas.itemconfig(self.rectangles[y][x], fill=couleur)
                    self.etat_affiche[y][x] = vivante

        self.texte_generation.set(f"Génération : {self.grille.generation}")
        self.texte_population.set(f"Population : {self.grille.population()}")

    # ------------------------------------------------------------------
    # Animation
    # ------------------------------------------------------------------
    def etape(self):
        """Avance d'une génération et rafraîchit l'affichage."""
        self.grille.generation_suivante()
        self.dessiner()

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
        """Calcule une génération puis se reprogramme elle-même avec after()."""
        self.etape()
        delai_ms = 1000 // self.vitesse.get()
        self.id_minuteur = self.fenetre.after(delai_ms, self._boucle)

    # ------------------------------------------------------------------
    # Actions sur la grille
    # ------------------------------------------------------------------
    def remplir_aleatoirement(self):
        self.grille.remplir_aleatoirement(0.25)
        self.dessiner()

    def effacer(self):
        self.arreter()
        self.grille.vider()
        self.dessiner()

    def changer_torique(self):
        self.grille.changer_torique(self.torique.get())

    def placer_motif(self, x, y):
        """Place le motif choisi centré sur la case (x, y)."""
        motif = MOTIFS[self.motif_choisi.get()]
        largeur, hauteur = dimensions_motif(motif)
        self.grille.placer_motif(motif, x - largeur // 2, y - hauteur // 2)
        self.dessiner()

    def placer_motif_au_centre(self):
        self.placer_motif(self.grille.largeur // 2, self.grille.hauteur // 2)

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
        if self.grille.est_dans_grille(x, y):
            cellule = self.grille.get_cellule(x, y)
            self.mode_dessin = not cellule.est_vivante()
            self._peindre(cellule)

    def glisser(self, evenement):
        x, y = self._case_sous_souris(evenement)
        if self.grille.est_dans_grille(x, y):
            self._peindre(self.grille.get_cellule(x, y))

    def _peindre(self, cellule):
        if self.mode_dessin:
            cellule.naitre()
        else:
            cellule.mourir()
        self.dessiner()

    def placer_motif_a_la_souris(self, evenement):
        x, y = self._case_sous_souris(evenement)
        if self.grille.est_dans_grille(x, y):
            self.placer_motif(x, y)

    # ------------------------------------------------------------------
    def lancer(self):
        """Ouvre la fenêtre et lance la boucle d'événements de Tkinter."""
        self.fenetre.mainloop()
