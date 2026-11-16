"""
Module motifs : quelques motifs célèbres du jeu de la vie.

Chaque motif est une liste de chaînes de caractères :
  "O" = cellule vivante, "." = cellule morte.
"""

MOTIFS = {
    # --- Oscillateurs ---------------------------------------------------
    "Clignotant": [
        "OOO",
    ],
    "Crapaud": [
        ".OOO",
        "OOO.",
    ],
    "Pulsar": [
        "..OOO...OOO..",
        ".............",
        "O....O.O....O",
        "O....O.O....O",
        "O....O.O....O",
        "..OOO...OOO..",
        ".............",
        "..OOO...OOO..",
        "O....O.O....O",
        "O....O.O....O",
        "O....O.O....O",
        ".............",
        "..OOO...OOO..",
    ],
    "Pentadécathlon": [
        "..O....O..",
        "OO.OOOO.OO",
        "..O....O..",
    ],
    # --- Vaisseaux (motifs qui se déplacent) ------------------------------
    "Planeur": [
        ".O.",
        "..O",
        "OOO",
    ],
    "Vaisseau léger": [
        ".O..O",
        "O....",
        "O...O",
        "OOOO.",
    ],
    # --- Canon : produit un planeur toutes les 30 générations -------------
    "Canon de Gosper": [
        "........................O...........",
        "......................O.O...........",
        "............OO......OO............OO",
        "...........O...O....OO............OO",
        "OO........O.....O...OO..............",
        "OO........O...O.OO....O.O...........",
        "..........O.....O.......O...........",
        "...........O...O....................",
        "............OO......................",
    ],
    # --- Mathusalems : petits motifs qui évoluent très longtemps ----------
    "R-pentomino": [
        ".OO",
        "OO.",
        ".O.",
    ],
    "Gland": [
        ".O.....",
        "...O...",
        "OO..OOO",
    ],
    "Diehard": [          # disparaît complètement au tour 130
        "......O.",
        "OO......",
        ".O...OOO",
    ],
}


def coordonnees_motif(motif):
    """Renvoie la liste des positions (dx, dy) des cellules vivantes du motif.

    >>> coordonnees_motif([".O", "O."])
    [(1, 0), (0, 1)]
    """
    positions = []
    for dy, ligne in enumerate(motif):
        for dx, caractere in enumerate(ligne):
            if caractere == "O":
                positions.append((dx, dy))
    return positions


def dimensions_motif(motif):
    """Renvoie (largeur, hauteur) du motif."""
    largeur = max(len(ligne) for ligne in motif)
    hauteur = len(motif)
    return largeur, hauteur
