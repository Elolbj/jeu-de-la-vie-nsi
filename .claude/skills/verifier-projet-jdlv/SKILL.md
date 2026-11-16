---
name: verifier-projet-jdlv
description: Vérifie le projet « Jeu de la vie » de Terminale NSI (classes Cellule, Jdlv, Jdlv_IHM) avant de le rendre ou après une modification - exigences du sujet (attribut Etat entier, tableau 2D grille, attribut tour, méthode start, classe Jdlv_IHM), tests, docstrings, animation Tkinter sans boucle while, capture d'écran de la fenêtre, version web pour téléphone (moteur JavaScript comparé à un calcul de référence, damier géant, affichage mobile), cohérence du README. À utiliser dès que l'on modifie ce projet (code Python ou page web), qu'on change la taille du damier, ou quand l'utilisateur demande si son jeu de la vie est « bon », « conforme au sujet », « prêt à rendre », « marche sur téléphone », veut lancer les tests ou prépare l'oral, même s'il ne dit pas « vérifier ».
---

# Vérifier le projet Jeu de la vie (Terminale NSI)

Le projet sera noté sur : le fonctionnement, la qualité du code (commentaires,
modularité), les tests et l'originalité. Le sujet impose des noms précis ; un
nom changé « pour faire propre » (par exemple `Etat` en `etat` pour suivre
PEP 8) fait perdre des points, même si le programme marche. Cette vérification
sert à attraper ce genre d'écart avant le rendu.

## Étapes

1. **Lancer le vérificateur** depuis la racine du projet :

   ```bash
   python .claude/skills/verifier-projet-jdlv/scripts/verifier.py .
   ```

   Il contrôle les exigences du sujet, lance les tests (pytest s'il est
   installé, sinon `python test_jeu_de_la_vie.py`) et signale les fonctions
   sans docstring ainsi que les boucles `while` dans l'IHM Tkinter (une telle
   boucle fige la fenêtre : il faut `after()`).
   Code de sortie 0 = conforme. `ATTENTION` n'est pas bloquant, `ÉCHEC` l'est.

   Si Tkinter manque pour le Python par défaut, relancer avec un autre
   interpréteur qui l'a (par exemple `python3.12`) pour vérifier `Jdlv_IHM`.

2. **Corriger chaque ÉCHEC** sans renommer les éléments imposés par le sujet :
   `Cellule.Etat` (entier 0/1), `Jdlv` avec un tableau 2D de `Cellule` et un
   attribut `tour` à 0, `Jdlv.start()`, classe `Jdlv_IHM`.
   Rester au niveau Terminale : pas de numpy, pas d'héritage obligatoire
   (hors programme), du code commenté en français.

3. **Si l'interface graphique a changé**, regarder la fenêtre :

   ```bash
   xvfb-run -a -s "-screen 0 1280x800x24" python scripts/capture.py <projet> <image.png>
   ```

   (chemin du script relatif au dossier de cette skill). Ouvrir l'image et
   vérifier que rien n'est coupé et que la courbe et les statistiques s'affichent.

4. **Si la version web (`web/jeu_de_la_vie.html`) a changé**, la tester :

   ```bash
   node .claude/skills/verifier-projet-jdlv/scripts/tester_web.js . [capture.png]
   ```

   Le script compare le moteur JavaScript, tour après tour, à un calcul de
   référence indépendant (tore et bords fermés), vérifie le diehard (éteint au
   tour 130) et le pentadécathlon (période 15), chronomètre un damier de
   2 000 × 2 000 cases, puis, si Playwright est installé, ouvre la page sur un
   iPhone simulé : pas d'erreur JavaScript, pas de défilement horizontal,
   animation qui avance. Une version web qui « a l'air de marcher » peut
   calculer faux sur les bords : c'est la comparaison avec la référence qui
   le montre.

   La page web n'utilise pas d'objet `Cellule` par case (trop lourd pour des
   millions de cases sur un téléphone) : c'est voulu, ne pas « corriger ». Le
   rendu noté est le code Python.

5. **Vérifier le README** : le nombre de tests annoncé, le tableau
   « Ce que demande le sujet » et la liste des fonctionnalités doivent
   correspondre au code.

## Compte rendu

Répondre en français, avec des mots simples (l'utilisateur est lycéen) :
un tableau « vérification / résultat », puis ce qui a été corrigé, puis ce qui
reste à faire. Citer la ligne de sortie des tests telle quelle.
