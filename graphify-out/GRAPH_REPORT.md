# Graph Report - jeu-de-la-vie-nsi  (2026-11-16)

## Corpus Check
- Corpus is ~24,982 words - fits in a single context window. You may not need a graph.

## Summary
- 358 nodes · 899 edges · 17 communities (9 shown, 8 thin omitted)
- Extraction: 96% EXTRACTED · 4% INFERRED · 0% AMBIGUOUS · INFERRED: 39 edges (avg confidence: 0.81)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- Classe Cellule et modules
- Variantes de règles
- Histoire et motifs célèbres
- Tests des motifs
- Calcul du tour suivant
- Bords et modifications du tableau
- Format RLE
- Attendus NSI et qualité
- Construction de la fenêtre
- Affichage console
- Vérificateur du projet
- Rendu et statut

## God Nodes (most connected - your core abstractions)
1. `Jdlv_IHM` - 53 edges
2. `Jdlv` - 48 edges
3. `Analyse algorithmique du jeu de la vie` - 48 edges
4. `README – Jeu de la vie, projet POO Terminale NSI` - 44 edges
5. `Variantes de règles et extensions du Jeu de la vie` - 43 edges
6. `Cellule` - 25 edges
7. `Regle` - 22 edges
8. `jeu_avec()` - 19 edges
9. `MOTIFS (motifs célèbres)` - 17 edges
10. `Jdlv_IHM_Console` - 15 edges

## Surprising Connections (you probably didn't know these)
- `tour_suivant_reference()` --semantically_similar_to--> `Représentation « ensemble des vivantes + Counter »`  [INFERRED] [semantically similar]
  test_jeu_de_la_vie.py → /home/user/jeu-de-la-vie-nsi/research_notes/Originalité jeu de la vie NSI/analyse_algorithmique.md
- `Attendus NSI (Terminale) pour un projet POO Jeu de la vie` --references--> `Cellule`  [INFERRED]
  /home/user/jeu-de-la-vie-nsi/research_notes/Originalité jeu de la vie NSI/attendus_nsi.md → cellule.py
- `Capture d'écran de Jdlv_IHM (canon de Gosper, pentadécathlons, pulsar, couleurs selon l'âge)` --references--> `Jdlv_IHM`  [INFERRED]
  /home/user/jeu-de-la-vie-nsi/docs/capture.png → jdlv_ihm.py
- `Variantes de règles et extensions du Jeu de la vie` --conceptually_related_to--> `lire_rle()`  [INFERRED]
  /home/user/jeu-de-la-vie-nsi/research_notes/Originalité jeu de la vie NSI/variantes_et_extensions.md → rle.py
- `Attendus NSI (Terminale) pour un projet POO Jeu de la vie` --conceptually_related_to--> `test_entrees_invalides()`  [INFERRED]
  /home/user/jeu-de-la-vie-nsi/research_notes/Originalité jeu de la vie NSI/attendus_nsi.md → test_jeu_de_la_vie.py

## Import Cycles
- None detected.

## Communities (17 total, 8 thin omitted)

### Community 0 - "Classe Cellule et modules"
Cohesion: 0.05
Nodes (18): capture.py (script de capture d'écran), capturer(), Cellule, capturer(), Jdlv, Jdlv.placer_motif(), Jdlv.remplir_aleatoirement(), main() (+10 more)

### Community 1 - "Variantes de règles"
Cohesion: 0.09
Nodes (37): Âge des cellules (tours consécutifs en vie), Automates cellulaires « Life-like » (2^18 règles), Brian's Brain (automate à 3 états), CONWAY (Regle B3/S23), Coloration des cellules selon l'âge, Coral B3/S45678, Courbe de population, Day & Night B3678/S34678 (+29 more)

### Community 2 - "Histoire et motifs célèbres"
Cohesion: 0.10
Nodes (39): Algorithme de Brent, Algorithme de Floyd (lièvre et tortue), Analyse algorithmique du jeu de la vie, Bill Gosper, Canon de Gosper, Capture d'écran de Jdlv_IHM (canon de Gosper, pentadécathlons, pulsar, couleurs selon l'âge), Charles Corderman, Conjecture de Conway sur la croissance bornée (prix de 50 $) (+31 more)

### Community 3 - "Tests des motifs"
Cohesion: 0.14
Nodes (22): Bloc (block), Clignotant (blinker), Retour d'un planeur sur un tore après 4·ppcm(L, H) générations, Planeur (glider), avancer_jusqu_a_stabilisation(), cases_vivantes(), doit_echouer(), jeu_avec() (+14 more)

### Community 4 - "Calcul du tour suivant"
Cohesion: 0.11
Nodes (5): Comparaison avec une implémentation de référence, Mise à jour en deux étapes (calcul puis application), Retour arrière (historique des tours), test_comparaison_avec_une_implementation_de_reference(), tour_suivant_reference()

### Community 5 - "Bords et modifications du tableau"
Cohesion: 0.14
Nodes (6): Bouteille de Klein (bord inversé), Grille bornée (bords morts), Jdlv.changer_torique(), test_modifier_une_cellule_relance_la_detection(), test_nombre_de_voisines(), Topologie torique (bords reliés, modulo)

### Community 6 - "Format RLE"
Cohesion: 0.17
Nodes (7): _decoder(), ecrire_fichier_rle(), ecrire_rle(), _lire_entete(), lire_fichier_rle(), lire_rle(), test_ecriture_rle_aller_retour()

### Community 7 - "Attendus NSI et qualité"
Cohesion: 0.17
Nodes (12): Attendus NSI (Terminale) pour un projet POO Jeu de la vie, Docstrings (PEP 257), doctest, Grille d'évaluation d'un projet NSI, Oral de projet (Grand oral), PEP 8, pytest, etat_suivant() (+4 more)

### Community 11 - "Vérificateur du projet"
Cohesion: 0.25
Nodes (5): charger(), lancer_tests(), main(), verifier_qualite(), verifier_sujet()

## Ambiguous Edges - Review These
- `capture.py (script de capture d'écran)` → `Capture d'écran de Jdlv_IHM (canon de Gosper, pentadécathlons, pulsar, couleurs selon l'âge)`  [AMBIGUOUS]
  /home/user/jeu-de-la-vie-nsi/docs/capture.png · relation: conceptually_related_to

## Knowledge Gaps
- **1 isolated node(s):** `Vidéo « Voyages au pays des maths » (Arte)`
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 117 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **8 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Jdlv_IHM` connect `Construction de la fenêtre` to `Classe Cellule et modules`, `Variantes de règles`, `Histoire et motifs célèbres`, `Bords et modifications du tableau`, `Attendus NSI et qualité`, `Boucle d'animation`, `Affichage console`, `Règles et fichiers dans l'IHM`, `Dessin à la souris`, `Rendu et statut`, `Pause et retour arrière`, `Placement de motifs`?**
  _High betweenness centrality (0.297) - this node is a cross-community bridge._
- **Are the 2 inferred relationships involving `Jdlv_IHM` (e.g. with `Capture d'écran de Jdlv_IHM (canon de Gosper, pentadécathlons, pulsar, couleurs selon l'âge)` and `Jdlv`) actually correct?**
  _`Jdlv_IHM` has 2 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Vidéo « Voyages au pays des maths » (Arte)` to the rest of the system?**
  _1 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Classe Cellule et modules` be split into smaller, more focused modules?**
  _Cohesion score 0.05087719298245614 - nodes in this community are weakly interconnected._
- **Why does `Jdlv` connect `Classe Cellule et modules` to `Variantes de règles`, `Histoire et motifs célèbres`, `Tests des motifs`, `Calcul du tour suivant`, `Bords et modifications du tableau`, `Construction de la fenêtre`, `Affichage console`, `Dessin à la souris`, `Rendu et statut`?**
  _High betweenness centrality (0.250) - this node is a cross-community bridge._
- **Are the 4 inferred relationships involving `Jdlv` (e.g. with `Jdlv_IHM_Console` and `Jdlv_IHM`) actually correct?**
  _`Jdlv` has 4 INFERRED edges - model-reasoned connections that need verification._

### Low-confidence Hints
_AMBIGUOUS edges — the extractor was unsure. Verify before acting on these._

- **What is the exact relationship between `capture.py (script de capture d'écran)` and `Capture d'écran de Jdlv_IHM (canon de Gosper, pentadécathlons, pulsar, couleurs selon l'âge)`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._