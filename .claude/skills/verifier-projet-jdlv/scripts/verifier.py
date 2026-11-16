"""
Vérifie que le projet « Jeu de la vie » respecte le sujet de Terminale NSI
et donne un bilan de qualité.

Usage : python verifier.py [dossier_du_projet]
Code de sortie : 0 si toutes les exigences du sujet sont respectées, 1 sinon.
"""

import ast
import importlib
import importlib.util
import os
import subprocess
import sys

OK, ECHEC, ATTENTION = "OK", "ÉCHEC", "ATTENTION"


def charger(module):
    """Importe un module du projet ; renvoie (module, message d'erreur)."""
    try:
        return importlib.import_module(module), None
    except Exception as erreur:          # on veut un bilan, pas un plantage
        return None, f"{type(erreur).__name__}: {erreur}"


def verifier_sujet():
    """Exigences du sujet. Renvoie une liste de (statut, message)."""
    bilan = []
    cellule, erreur = charger("cellule")
    if cellule is None or not hasattr(cellule, "Cellule"):
        return [(ECHEC, f"classe Cellule introuvable dans cellule.py ({erreur})")]
    c = cellule.Cellule()
    ok = isinstance(getattr(c, "Etat", None), int) and c.Etat == 0
    bilan.append((OK if ok else ECHEC, "Cellule().Etat est un entier valant 0 (morte)"))

    jdlv, erreur = charger("jdlv")
    if jdlv is None or not hasattr(jdlv, "Jdlv"):
        return bilan + [(ECHEC, f"classe Jdlv introuvable dans jdlv.py ({erreur})")]
    jeu = jdlv.Jdlv(6, 5)
    tableau = None
    for nom, valeur in vars(jeu).items():   # cherche un attribut liste de listes de Cellule
        if isinstance(valeur, list) and valeur and all(
                isinstance(l, list) and l and all(isinstance(x, cellule.Cellule) for x in l)
                for l in valeur):
            tableau = nom
    bilan.append((OK if tableau else ECHEC,
                  f"Jdlv a un tableau 2D de Cellule (attribut : {tableau})"))
    bilan.append((OK if getattr(jeu, "tour", None) == 0 else ECHEC,
                  "Jdlv.tour vaut 0 au départ"))
    bilan.append((OK if callable(getattr(jeu, "start", None)) else ECHEC,
                  "Jdlv a une méthode start()"))

    ihm, erreur = charger("jdlv_ihm")
    if ihm is None and "tkinter" in str(erreur).lower():
        bilan.append((ATTENTION, "Jdlv_IHM non vérifiable : Tkinter absent sur cette machine"))
    else:
        bilan.append((OK if ihm and hasattr(ihm, "Jdlv_IHM") else ECHEC,
                      f"classe Jdlv_IHM dans jdlv_ihm.py {erreur or ''}".strip()))
    return bilan


def verifier_qualite(dossier):
    """Docstrings manquantes et boucle while dans l'IHM. Renvoie (statut, message)."""
    bilan = []
    sans_doc = []
    for fichier in sorted(os.listdir(dossier)):
        if not fichier.endswith(".py") or fichier.startswith("test"):
            continue
        with open(os.path.join(dossier, fichier), encoding="utf-8") as f:
            arbre = ast.parse(f.read())
        if ast.get_docstring(arbre) is None:
            sans_doc.append(f"{fichier} (module)")
        for noeud in ast.walk(arbre):
            if isinstance(noeud, (ast.FunctionDef, ast.ClassDef)) \
                    and not noeud.name.startswith("__") \
                    and ast.get_docstring(noeud) is None:
                sans_doc.append(f"{fichier}:{noeud.lineno} {noeud.name}")
    bilan.append((OK if not sans_doc else ATTENTION,
                  "docstrings présentes partout" if not sans_doc
                  else f"{len(sans_doc)} élément(s) sans docstring : " + ", ".join(sans_doc)))

    chemin_ihm = os.path.join(dossier, "jdlv_ihm.py")
    if os.path.exists(chemin_ihm):
        with open(chemin_ihm, encoding="utf-8") as f:
            arbre = ast.parse(f.read())
        boucles = [n.lineno for n in ast.walk(arbre) if isinstance(n, ast.While)]
        bilan.append((OK if not boucles else ATTENTION,
                      "pas de boucle while dans l'IHM Tkinter (after() est utilisé)" if not boucles
                      else f"boucle while dans jdlv_ihm.py ligne(s) {boucles} : risque de figer la fenêtre"))
    return bilan


def lancer_tests(dossier):
    """Lance pytest s'il est installé, sinon le fichier de tests directement."""
    if importlib.util.find_spec("pytest"):
        commande = [sys.executable, "-m", "pytest", "-q"]
    else:
        commande = [sys.executable, "test_jeu_de_la_vie.py"]
    resultat = subprocess.run(commande, cwd=dossier, capture_output=True, text=True)
    derniere = (resultat.stdout.strip().splitlines() or ["(aucune sortie)"])[-1]
    return [(OK if resultat.returncode == 0 else ECHEC, f"tests : {derniere}")]


def main():
    dossier = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else ".")
    sys.path.insert(0, dossier)
    os.chdir(dossier)
    sections = [("Sujet", verifier_sujet()), ("Tests", lancer_tests(dossier)),
                ("Qualité", verifier_qualite(dossier))]
    echec = False
    for titre, bilan in sections:
        print(f"== {titre}")
        for statut, message in bilan:
            print(f"  [{statut}] {message}")
            echec = echec or (statut == ECHEC)
    print("\nRésultat :", "des exigences ne sont pas respectées" if echec else "conforme au sujet")
    sys.exit(1 if echec else 0)


if __name__ == "__main__":
    main()
