"""
Module rle : lecture et écriture de motifs au format RLE (Run Length Encoded).

C'est le format standard des passionnés du jeu de la vie (LifeWiki, Golly) :
des milliers de motifs sont disponibles sous cette forme. Exemple, le planeur :

    #N Planeur
    x = 3, y = 3, rule = B3/S23
    bob$2bo$3o!

  - les lignes qui commencent par # sont des commentaires ;
  - la ligne d'en-tête donne la largeur x, la hauteur y et la règle ;
  - b = cellule morte, o = cellule vivante, $ = fin de ligne, ! = fin du motif ;
  - un nombre devant un symbole le répète : 3o = ooo, 2$ = deux fins de ligne.

Un motif est représenté, comme dans motifs.py, par une liste de chaînes
où "O" est une cellule vivante et "." une cellule morte.
"""

LONGUEUR_LIGNE_MAX = 70   # les fichiers RLE coupent les lignes à 70 caractères


# ----------------------------------------------------------------------
# Lecture
# ----------------------------------------------------------------------
def lire_rle(texte):
    """Analyse un texte au format RLE.

    Renvoie un couple (motif, regle) : motif est une liste de chaînes,
    regle est la notation B/S lue dans l'en-tête (ou None si absente).
    Lève ValueError si le texte n'est pas un RLE valide.
    """
    largeur = 0
    regle = None
    donnees = ""
    for ligne in texte.splitlines():
        ligne = ligne.strip()
        if ligne == "" or ligne.startswith("#"):
            continue                              # ligne vide ou commentaire
        if ligne.startswith("x"):
            largeur, regle = _lire_entete(ligne)
        else:
            donnees += ligne

    motif = _decoder(donnees)
    largeur = max([largeur] + [len(l) for l in motif])
    # Toutes les lignes doivent avoir la même longueur : on complète avec des "."
    return [ligne.ljust(largeur, ".") for ligne in motif], regle


def _lire_entete(ligne):
    """'x = 3, y = 3, rule = B3/S23' -> (3, 'B3/S23')."""
    largeur = 0
    regle = None
    for morceau in ligne.split(","):
        cle, _, valeur = morceau.partition("=")
        cle = cle.strip().lower()
        valeur = valeur.strip()
        if cle == "x":
            largeur = int(valeur)
        elif cle == "rule":
            regle = convertir_regle(valeur)
    return largeur, regle


def convertir_regle(texte):
    """Ramène une règle RLE à la notation B/S utilisée par regle.py.

    'B3/S23' et 'b3/s23' restent tels quels ; l'ancienne notation '23/3'
    (survie/naissance) devient 'B3/S23'. Ce qui suit ':' (forme du tableau
    dans Golly) est ignoré.
    """
    texte = texte.split(":")[0].strip().upper()
    morceaux = texte.split("/")
    if len(morceaux) == 2 and not texte.startswith("B"):
        survie, naissance = morceaux
        if survie.startswith("S"):          # forme 'S23/B3'
            survie, naissance = survie[1:], naissance[1:]
        return f"B{naissance}/S{survie}"
    return texte


def _decoder(donnees):
    """Transforme 'bob$2bo$3o!' en ['.O', '..O', 'OOO']."""
    motif = []
    ligne = ""
    nombre = ""                    # chiffres lus avant un symbole
    for caractere in donnees:
        if caractere.isdigit():
            nombre += caractere
            continue
        repetitions = int(nombre) if nombre else 1
        nombre = ""
        if caractere == "b" or caractere == ".":
            ligne += "." * repetitions
        elif caractere == "$":
            motif.append(ligne)
            for _ in range(repetitions - 1):
                motif.append("")         # 3$ = deux lignes vides en plus
            ligne = ""
        elif caractere == "!":
            break
        elif caractere.isalpha():
            # 'o' (ou une lettre d'un automate à plusieurs états) = vivante
            ligne += "O" * repetitions
        else:
            raise ValueError(f"caractère inattendu dans le RLE : {caractere!r}")
    motif.append(ligne)
    return motif


def lire_fichier_rle(chemin):
    """Lit un fichier .rle et renvoie (motif, regle)."""
    with open(chemin, encoding="utf-8") as fichier:
        return lire_rle(fichier.read())


# ----------------------------------------------------------------------
# Écriture
# ----------------------------------------------------------------------
def ecrire_rle(motif, regle="B3/S23", nom=None):
    """Renvoie le texte RLE correspondant à un motif (liste de chaînes)."""
    # 1. On compte les répétitions : [[nombre, symbole], ...]
    sequences = []

    def ajouter(symbole):
        if sequences and sequences[-1][1] == symbole:
            sequences[-1][0] += 1          # même symbole : on augmente le compte
        else:
            sequences.append([1, symbole])

    for numero, ligne in enumerate(motif):
        if numero > 0:
            ajouter("$")
        for caractere in ligne.rstrip("."):   # inutile d'écrire les morts en fin de ligne
            ajouter("o" if caractere == "O" else "b")
    ajouter("!")

    # 2. On écrit chaque séquence ("3o", "b", "2$"...) en coupant les lignes
    lignes = []
    courante = ""
    for nombre, symbole in sequences:
        morceau = (str(nombre) if nombre > 1 else "") + symbole
        if len(courante) + len(morceau) > LONGUEUR_LIGNE_MAX:
            lignes.append(courante)
            courante = ""
        courante += morceau
    lignes.append(courante)

    largeur = max([len(l) for l in motif] + [0])
    entete = f"x = {largeur}, y = {len(motif)}, rule = {regle}"
    debut = [f"#N {nom}"] if nom else []
    return "\n".join(debut + [entete] + lignes) + "\n"


def ecrire_fichier_rle(chemin, motif, regle="B3/S23", nom=None):
    """Enregistre un motif dans un fichier .rle."""
    with open(chemin, "w", encoding="utf-8") as fichier:
        fichier.write(ecrire_rle(motif, regle, nom))
