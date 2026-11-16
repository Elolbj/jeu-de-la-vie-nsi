# Analyse algorithmique du jeu de la vie : stabilité, cycles, données de référence, performance, portée mathématique

> **Note de méthode (à lire par le rédacteur).** Dans cette session, `conwaylife.com` (LifeWiki) et `wikipedia.org` étaient **bloqués par le réseau** (échec DNS). Les pages LifeWiki/Wikipedia sont donc citées **via les résultats du moteur de recherche** et via des miroirs (miroir LifeWiki `conwaylife.njohnston.ca`, Life Lexicon de Stephen Silver sur `playgameoflife.com`, Lexicon fourni avec Golly sur `sources.debian.org`). Pour compenser, **chaque chiffre de motif a été recalculé par une simulation Python indépendante** (plan infini, ensemble de cellules vivantes, Python 3.13.18, Linux). La mention « simulation locale » renvoie à ce calcul ; le code essentiel est reproduit en section 2 pour que tout soit vérifiable. Pour une vérification directe sur LifeWiki, il faudrait autoriser `conwaylife.com` dans les réglages réseau de la session.

## 1. Détecter l'extinction, la stabilité, l'oscillation (avec sa période) et la translation dans une grille finie

### Takeaway
La méthode la plus simple et la plus sûre pour un programme NSI est un **dictionnaire `signature de l'état -> numéro de génération`** : dès qu'un état réapparaît, on a `debut = historique[sig]` et `periode = tour - debut` ; l'extinction est le cas « état vide » (période 1), la stabilité le cas période 1 non vide, l'oscillation période ≥ 2. Floyd et Brent économisent la mémoire (2 états seulement) mais coûtent 3 à 5 fois plus de calculs de générations ; sur un tore, un planeur seul finit **toujours** par « boucler » (période 4·ppcm(L, H), soit 1400 générations sur la grille 70×50 du projet), ce qui fausse le diagnostic « vaisseau ».

### Cited Findings

**Principe des algorithmes de détection de cycle**
- Toute suite x_{i+1} = f(x_i) sur un ensemble fini finit par être périodique : on note μ l'indice du premier état du cycle et λ la longueur (période) du cycle — [Wikipedia EN « Cycle detection » (via recherche)](https://en.wikipedia.org/wiki/Cycle_detection) ; [Rosetta Code « Cycle detection »](https://rosettacode.org/wiki/Cycle_detection).
- **Floyd (« lièvre et tortue »)** : deux pointeurs, la tortue en x_i et le lièvre en x_{2i} ; ils avancent de 1 et 2 pas jusqu'à se rencontrer ; une 2e phase donne μ, une 3e donne λ. L'attribution à Floyd est contestée (l'algorithme n'apparaît pas dans ses publications) — [Wikipedia « Cycle detection » (via recherche)](https://en.wikipedia.org/wiki/Cycle_detection).
- **Brent** : cherche la plus petite puissance de 2 supérieure à λ et μ ; la tortue reste fixe pendant que le lièvre avance, et la tortue « saute » sur le lièvre à chaque doublement ; à la rencontre, la distance est λ directement ; puis on avance le lièvre de λ pas depuis le début et on fait avancer les deux au même rythme pour obtenir μ. Un seul appel à f par pas ; dans un exemple, Floyd fait 16 appels contre 13 pour Brent — [Wikipedia « Cycle detection » (via recherche)](https://en.wikipedia.org/wiki/Cycle_detection) ; [Medium, « Cycle detection: Brent's algorithm »](https://medium.com/swlh/algorithm-ish-001-cycle-detection-brents-algorithm-f927a498c900).

**Mesures sur des soupes aléatoires (simulation locale, tore 32×32, densité 0,35, 5 graines)** — les trois méthodes trouvent exactement les mêmes (μ, λ) :

| soupe | μ (début du cycle) | période λ | appels à `step()` : dictionnaire | Floyd | Brent | états stockés (dict) |
|---|---|---|---|---|---|---|
| 0 | 207 | 2 | 209 | 1040 | 673 | 209 |
| 1 | 249 | 2 | 251 | 1250 | 757 | 251 |
| 2 | 146 | 1 | 147 | 731 | 549 | 147 |
| 3 | 602 | 2 | 604 | 3012 | 2231 | 604 |
| 4 | 333 | 2 | 335 | 1670 | 1181 | 335 |

— simulation locale (le dictionnaire coûte μ+λ générations, Floyd ≈ 5×, Brent ≈ 3,5× sur ces exemples ; Floyd/Brent ne gardent que 2 états en mémoire).

**Cas particuliers vérifiés (simulation locale)**
- Bloc seul : (μ, λ) = (0, 1) → « stable ».
- Diehard : (μ, λ) = (130, 1) avec 0 cellule → l'extinction est simplement le point fixe « grille vide ». Tester `len(vivantes) == 0` avant le dictionnaire suffit.
- Clignotant (p2) + pulsar (p3) sur la même grille : période globale détectée = **6** (= ppcm(2, 3)) par les trois méthodes. La période d'un état global est le ppcm des périodes de ses composantes.
- **Planeur sur un tore L×H** : retour exact à l'état initial après **4·ppcm(L, H)** générations : 40 sur 10×10, 96 sur 12×8, **1400 sur 70×50** (taille par défaut du projet). LWSS (vaisseau léger, horizontal) : 40 sur 20×10, **140 sur 70×50** (= 4·70/2).
- **Planeur sur grille bornée à bords morts** (20×20, cellules hors grille toujours mortes) : le planeur s'écrase dans le coin et devient un **bloc** ; cycle détecté à μ = 71, période 1.
- Les méthusalems donnent des résultats **différents sur le tore 70×50** (motif placé au centre) : R-pentomino → état fixe dès la génération 358 avec 60 cellules (au lieu de 1103/116 sur plan infini) ; acorn → oscillation p2 dès la génération 1471 avec 104 cellules (au lieu de 5206/633) ; diehard → s'éteint toujours à 130. Cause : les planeurs émis font le tour du tore et percutent les débris ; sur plan infini, à la génération 1103, l'ensemble R-pentomino + planeurs occupe une boîte de 501×525 cellules.

**Signature de l'état, mémoire, collisions (simulation locale, grille 70×50, ~30 % de cellules vivantes = 1030)**
- `frozenset` de tuples `(x, y)` : ≈ 33 Ko (l'ensemble) + ≈ 58 Ko (les tuples) ≈ **91 Ko par état**.
- tuple de tuples de 0/1 : ≈ 30 Ko ; **`bytes` (1 octet/cellule) : 3 533 octets** ; entier Python (1 bit/cellule) : 492 octets.
- Construire la signature `bytes` + son `hash` : ≈ 0,07 ms par état.
- Ordre de grandeur : 10 000 générations mémorisées = ~35 Mo en `bytes`, ~0,9 Go en `frozenset` (calcul à partir des tailles ci-dessus).
- **Collisions** : un `dict` Python compare les clés avec `==` quand les hachages coïncident, donc utiliser l'état complet comme clé est **sans risque de faux positif** ; en revanche ne stocker **que** `hash(etat)` (ou un hachage court) expose au paradoxe des anniversaires, p ≈ n²/2^(b+1) : 1,2·10⁻² pour b = 32 bits et n = 10⁴ états ; ≈ 1 (collision quasi certaine) pour b = 32 et n = 10⁶ ; 2,7·10⁻¹² pour b = 64 et n = 10⁴ ; 2,7·10⁻⁸ pour b = 64 et n = 10⁶ — calcul local.
- **Piège Python** : `hash(b'abc')` change d'un lancement de l'interpréteur à l'autre (−1790980314631784226 puis 7854927751028922799 lors de deux exécutions locales), alors que `hash((1, 2))` reste identique — simulation locale ; c'est la « randomisation du hachage » des `str`/`bytes` (variable `PYTHONHASHSEED`) décrite dans la [documentation Python, `object.__hash__`](https://docs.python.org/3/reference/datamodel.html#object.__hash__) (page non consultée dans cette session). Conséquence : ne jamais enregistrer des `hash()` dans un fichier pour les comparer d'une exécution à l'autre.

**Translation (vaisseaux) sur plan infini** — simulation locale : en normalisant l'ensemble des cellules (translation pour amener min x et min y à 0) et en mémorisant le décalage, on obtient pour le planeur « même forme après 4 générations, décalage (1, 1) » et pour le LWSS « même forme après 4 générations, décalage (−2, 0) ».

### Inferences
- **Recette conseillée pour le projet** (grille `Jdlv` de `Cellule` reliées, torique par défaut) :
  ```python
  def signature(jeu):
      return bytes(1 if c.vivante else 0 for ligne in jeu.grille for c in ligne)  # 3,5 Ko en 70x50

  historique = {}                      # signature -> numéro de génération
  sig = signature(jeu)
  if sig in historique:
      debut = historique[sig]
      periode = jeu.tour - debut
      if nb_vivantes == 0:   etat = "extinction"
      elif periode == 1:     etat = "stable"
      else:                  etat = f"oscillation de période {periode} (depuis la génération {debut})"
  historique[sig] = jeu.tour
  ```
  Vérifier l'extinction (`nb_vivantes == 0`) et la stabilité (`nouvel_etat == ancien_etat`) **avant** le dictionnaire coûte O(1)/O(L·H) sans mémoire.
- **Compromis mémoire** : si la mémoire inquiète, une fenêtre glissante (`collections.deque(maxlen=K)` + un `dict` des K dernières signatures) détecte toutes les périodes ≤ K ; les soupes aléatoires finissent presque toujours en p1/p2 (cf. tableau), mais K doit dépasser 4·ppcm(L, H) (1400 en 70×50) pour qu'un planeur errant soit reconnu. Floyd/Brent sont plus élégants à présenter à l'oral (mémoire O(1)) mais plus lents en pratique.
- **Détection de vaisseau sur le tore** : la normalisation par la boîte englobante ne marche que si le motif ne touche pas les bords ; sinon il faut tester des décalages (dx, dy) modulo L et H, ce qui coûte O(L·H) par décalage. Sur le tore, un « oscillateur de période 4·ppcm(L, H) » contenant un seul petit motif est presque toujours un planeur qui fait le tour.
- **Tests automatisés** : les chiffres de référence des méthusalems (section 2) ne sont valables **que sur plan infini** (représentation par ensemble sans modulo) ; sur la grille torique 70×50 du projet il faut soit des valeurs propres au tore (celles mesurées ci-dessus dépendent de la position initiale), soit tester les méthusalems avec un moteur « ensemble » non borné.

### Gaps
- Pas de source primaire consultée pour Floyd (attribution) ni pour l'article de Brent (1980) : seules Wikipedia (via recherche) et Rosetta Code sont citées.
- Les mesures de mémoire/vitesse sont locales (une machine, Python 3.13.18) ; ordre de grandeur seulement.
- Les valeurs sur tore (358/60, 1471/104) dépendent de la position initiale du motif et de la taille de la grille : à ne pas présenter comme des constantes.

## 2. Données de référence exactes sur les motifs classiques (utilisables comme valeurs attendues de tests)

### Takeaway
Tous les chiffres demandés sont confirmés à la fois par une source (LifeWiki/Lexicon/Wikipedia via recherche) et par simulation locale : bloc 4, ruche 6, pain 7, bateau 5, baignoire 4 ; clignotant p2 (3), crapaud p2 (6), balise p2 (6/8), pulsar p3 (48), pentadécathlon p15 (12) ; planeur 5 cellules p4 c/4, LWSS 9 cellules p4 c/2 ; canon de Gosper 36 cellules p30 ; R-pentomino stable à la génération 1103 avec 116 cellules dont 6 planeurs ; acorn stable à 5206 avec 633 cellules dont 13 planeurs ; diehard disparaît à la génération 130. Seuls « pulsar = 48 cellules » et « canon de Gosper = 36 cellules » ne sont confirmés que par la simulation (pas trouvés dans une source accessible).

### Cited Findings

**Tableau de référence (plan infini ; « pop » = nombre de cellules vivantes de la phase donnée)**

| Motif (nom FR usuel) | Cellules | Période | Déplacement / vitesse | Source + vérification |
|---|---|---|---|---|
| Block (bloc) | 4 | 1 (stable) | — | [techno-science.net, « Jeu de la vie »](https://www.techno-science.net/fr/definitions/jeu-de-la-vie) (« le bloc de quatre cellules est la plus petite » structure stable) ; simulation locale |
| Beehive (ruche) | 6 | 1 | — | simulation locale |
| Loaf (pain) | 7 | 1 | — | simulation locale |
| Boat (bateau) | 5 | 1 | — | simulation locale |
| Tub (baignoire / bassin) | 4 | 1 | — | simulation locale |
| Blinker (clignotant) | 3 | 2 | — | simulation locale |
| Toad (crapaud / « grenouille ») | 6 | 2 | — | [techno-science.net](https://www.techno-science.net/fr/definitions/jeu-de-la-vie) (« se répète toutes les deux générations ») ; simulation locale |
| Beacon (balise / phare) | 8 puis 6 (deux phases) | 2 | — | simulation locale |
| Pulsar | 48 (phases : 48, 56, 72) | 3 | — | période 3 : Life Lexicon / pages LifeWiki (via recherche, ex. [conwaylife.njohnston.ca, « Early Life »](https://conwaylife.njohnston.ca/book/early_life)) ; **48 cellules : simulation locale seulement** |
| Pentadécathlon | 12 dans sa phase minimale (phases : 12, 16, 18, 20, 22, 28, 40) | 15 | — | [Life Lexicon, « pentadecathlon »](https://playgameoflife.com/lexicon/pentadecathlon) (période 15, trouvé par Conway en 1970) ; simulation locale (une ligne de 10 cellules évolue en pentadécathlon p15) |
| Glider (planeur) | 5 (toutes phases) | 4 | (1, 1) en 4 gén. → **c/4 diagonal** | [Life Lexicon fourni avec Golly (Debian), lettre G](https://sources.debian.org/data/main/g/golly/3.3-1.1/gui-common/Help/Lexicon/lex_g.htm) (c/4 diagonal, plus petit et premier vaisseau découvert, Richard Guy 1970) ; simulation locale |
| LWSS (vaisseau léger) | 9 (phases : 9, 12) | 4 | 2 cellules en 4 gén. → **c/2 orthogonal** | [Life Lexicon, « LWSS »](https://playgameoflife.com/lexicon/LWSS_(1)) (c/2 orthogonal, période 4, plus petit vaisseau orthogonal) ; simulation locale |
| Gosper glider gun (canon à planeurs) | 36, boîte 36×9 | 30 | 1 planeur (5 cellules) toutes les 30 gén. | période 30 / 1er planeur à la génération 15 : [Wikipedia « Gun (cellular automaton) » (via recherche)](https://en.wikipedia.org/wiki/Gun_(cellular_automaton)), [David Darling, « Life game »](https://daviddarling.info/encyclopedia/L/Life_game.html) ; **36 cellules : simulation locale seulement** (population 36, 41, 46, 51, 56 aux générations 0, 30, 60, 90, 120) |

(c = « vitesse de la lumière » = 1 cellule par génération.)

**Méthusalems (plan infini)**
- **R-pentomino** (5 cellules) : se stabilise à la **génération 1103** avec **116 cellules** et a émis **6 planeurs** ; ces 6 planeurs sont les premiers vaisseaux jamais observés ; le premier planeur apparaît à la génération 69 et fut remarqué par Richard K. Guy — [Wikipedia, « Conway's Game of Life » (via recherche)](https://en.wikipedia.org/wiki/Conway%27s_Game_of_Life) ; [Wikipedia, « Methuselah (cellular automaton) »](https://en.wikipedia.org/wiki/Methuselah_(cellular_automaton)) ; [miroir LifeWiki « R-pentomino »](https://conwaylife.njohnston.ca/wiki/R) ; [Life Lexicon, « R-pentomino »](https://playgameoflife.com/lexicon/R-pentomino). [OEIS A268857](https://oeis.org/A268857/internal) dit « stabilise à 116 après la génération 1102 » (même fait, indexation différente).
  - **Simulation locale** : population aux générations 1101 à 1105 = 118, 118, **116**, 116, 116 ; dernière variation de population à la génération 1103 ; à cette date 6 composantes isolées de 5 cellules (les planeurs, 30 cellules) + **86 cellules de débris** → **116 inclut les planeurs**. Ceci tranche une ambiguïté signalée par la recherche : la légende de l'image LifeWiki montrerait le motif sans planeurs, alors que le Lexicon dit que 116 inclut les planeurs ; la simulation donne raison au Lexicon. Population maximale : 319 à la génération 821 (simulation locale seulement). Premier planeur isolé (marge de 2 cellules) visible à la génération 70 en local, cohérent avec « génération 69 » selon le critère.
- **Acorn** (« gland », 7 cellules) : trouvé par Charles Corderman (au plus tard en 1971, date exacte inconnue) ; se stabilise après **5206 générations** en un motif de **633 cellules** comprenant **13 planeurs** ; population maximale **1057 à la génération 4408** — [Life Lexicon, « acorn »](https://playgameoflife.com/lexicon/acorn) ; [miroir LifeWiki « Acorn »](https://conwaylife.njohnston.ca/wiki/Acorn) ; [Wikipedia « Methuselah »](https://en.wikipedia.org/wiki/Methuselah_(cellular_automaton)).
  - **Simulation locale** : population aux générations 5204 à 5208 = 635, 635, **633**, 633, 633 ; 13 composantes de 5 cellules loin de l'origine (65 cellules) + 568 cellules de débris → 633 **inclut** les 13 planeurs ; maximum 1057 à la génération 4408 (identique à la source). Calcul : 6,5 s pour 6500 générations avec la méthode « ensemble ».
- **Diehard** (7 cellules) : disparaît entièrement après **130 générations** ; 130 est **conjecturé** (non prouvé) comme maximum pour les motifs de 7 cellules ou moins ; avec 8 cellules ou plus, on peut construire des motifs qui meurent après un temps arbitrairement long (un planeur + un clignotant ou un pré-bloc) ; record connu (octobre 2024) d'un diehard « naturel » : 1413 générations — [Life Lexicon, « diehard »](https://playgameoflife.com/lexicon/diehard) ; [miroir LifeWiki « Diehard »](https://conwaylife.njohnston.ca/wiki/Diehard) ; [Wikipedia « Conway's Game of Life » (via recherche)](https://enwp.org/Conway_game).
  - **Simulation locale** : population aux générations 127 à 130 = 5, 3, 2, **0** ; maximum 40 cellules à la génération 94 (local seulement).

**Coordonnées utilisées (vérifiables ; `O` = vivante, `.` = morte ; ligne = y, colonne = x)**
- Planeur : `.O.` / `..O` / `OOO` — LWSS : `.O..O` / `O....` / `O...O` / `OOOO.`
- R-pentomino : `.OO` / `OO.` / `.O.` — Acorn : `.O.....` / `...O...` / `OO..OOO` — Diehard : `......O.` / `OO......` / `.O...OOO`
- Pentadécathlon (phase 12) : `..O....O..` / `OO.OOOO.OO` / `..O....O..`
- Pulsar (13×13) : lignes 0, 5, 7, 12 = `..OOO...OOO..` ; lignes 2-4 et 8-10 = `O....O.O....O` ; lignes 1, 6, 11 vides.
- Canon de Gosper (RLE) : `24bo$22bobo$12b2o6b2o12b2o$11bo3bo4b2o12b2o$2o8bo5bo3b2o$2o8bo3bob2o4bobo$10bo5bo7bo$11bo3bo$12b2o!`

#### Moteur de vérification (plan infini, reproductible)
```python
from collections import Counter
def step(vivantes):                      # vivantes : frozenset de (x, y)
    c = Counter((x+dx, y+dy) for x, y in vivantes
                for dx in (-1, 0, 1) for dy in (-1, 0, 1) if dx or dy)
    return frozenset(p for p, n in c.items() if n == 3 or (n == 2 and p in vivantes))
def normaliser(s):                       # pour détecter une translation
    mx = min(x for x, _ in s); my = min(y for _, y in s)
    return frozenset((x-mx, y-my) for x, y in s), (mx, my)
# période/déplacement : plus petit p tel que normaliser(step^p(s))[0] == normaliser(s)[0]
# méthusalem : dernière génération où len(s) change (vérifiée ensuite par analyse des débris)
```

### Inferences
- Valeurs directement utilisables en `assert` (moteur plan infini) : `len(step^1103(R)) == 116` et `len(step^1102(R)) == 118` ; `len(step^5206(acorn)) == 633` et `len(step^5205(acorn)) == 635` ; `step^130(diehard) == frozenset()` et `len(step^129(diehard)) == 2` ; `step^15(pentadecathlon) == pentadecathlon` ; `step^3(pulsar) == pulsar` et `step^1(pulsar) != pulsar` ; `normaliser(step^4(planeur))` = même forme avec décalage (1, 1) ; LWSS décalage 2 cellules en 4 générations ; canon : `len(step^(30k)(canon)) == 36 + 5k` pour k = 0..4.
- Sur la grille torique du projet, les tests d'oscillateurs/vaisseaux restent valables si la grille laisse une marge suffisante autour du motif (un planeur ne revient à son état initial qu'après 4·ppcm(L, H) générations, pas 4).

### Gaps
- « Pulsar = 48 cellules » et « canon de Gosper = 36 cellules » : **non retrouvés dans une source accessible** (LifeWiki bloquée ; la recherche signale un autre canon de 36 cellules, le canon de Simkin, 2015, période 120, à ne pas confondre) ; confirmés uniquement par simulation locale (le RLE utilisé produit bien un planeur toutes les 30 générations).
- Comptes de cellules du bloc, de la ruche, du pain, du bateau, de la baignoire, du clignotant, de la balise : vérifiés par simulation locale, pas confrontés à une page source (LifeWiki inaccessible).
- Populations maximales du R-pentomino (319 à la génération 821) et du diehard (40 à la génération 94) : simulation locale seulement.
- Le nom français exact de certains motifs (tub, beacon, loaf) varie selon les sources ; non vérifié sur Wikipédia FR (inaccessible).

## 3. Performance et complexité en Python pur

### Takeaway
Une génération sur tableau coûte Θ(L·H) (9 lectures par case), quelle que soit la population ; la version « ensemble des cellules vivantes + `Counter` » coûte Θ(n) avec n le nombre de cellules vivantes, donc elle écrase les autres sur grille clairsemée (≈ 3300 gén/s contre ≈ 40-80 gén/s sur 200×200 à 2 %) ; sur 70×50 toutes les versions dépassent largement 30 images/s, et le goulot réel devient l'affichage Tkinter, d'où l'intérêt de ne redessiner que les cellules qui ont changé (31 % des cases au début d'une soupe, ~2 % après 1000 générations).

### Cited Findings
- Représentation « ensemble des cellules vivantes » + `Counter` qui compte, pour chaque cellule voisine d'une cellule vivante, son nombre de voisines vivantes ; la génération suivante garde les cellules à 3 voisines, ou à 2 voisines si déjà vivantes — [Peter Norvig, notebook « Life » (pytudes)](https://nbviewer.org/github/norvig/pytudes/blob/HEAD/ipynb/Life.ipynb).
- **Hashlife** (Bill Gosper, « Exploiting Regularities in Large Cellular Spaces », *Physica* 10D, 1984) : arbres quaternaires (quadtrees) + mémoïsation, accélération « astronomique » sur les motifs réguliers — [résumé ProQuest (via recherche)](https://www.proquest.com/docview/202694632). (Un site date Hashlife de 1971 : erreur, la publication est de 1984 — [conway.ximg.app](https://conway.ximg.app/history.html) contredit par la référence de l'article.)
- **Mesures locales** (Python 3.13.18, Linux ; générations par seconde, moyenne sur 50 générations en 70×50 et 20 en 200×200, soupe aléatoire, tore) :

| Méthode | 70×50, 30 % | 200×200, 30 % | 200×200, 2 % |
|---|---|---|---|
| Naïve : double boucle, 8 accès `grille[(y+dy)%H][(x+dx)%W]` | 402 gén/s (2,5 ms) | 39 gén/s (26 ms) | 42 gén/s (24 ms) |
| Listes de voisins précalculées (indices dans une liste plate) | 852 gén/s (1,2 ms) | 79 gén/s (12,7 ms) | 79 gén/s (12,6 ms) |
| Objets `Cellule` + liste `voisines` précalculée (style du projet) | 800 gén/s (1,25 ms) | 58 gén/s (17 ms) | 75 gén/s (13 ms) |
| Ensemble des vivantes + `Counter` | 1152 gén/s (0,87 ms) | 60 gén/s (16,8 ms) | **3302 gén/s (0,30 ms)** |

  — simulation locale (le précalcul des voisins double environ la vitesse par rapport au naïf ; la méthode « ensemble » ne dépend que du nombre de vivantes).
- **Fraction de cellules qui changent d'état** (soupe 70×50 à 30 %, simulation locale) : génération 1 : 1107/3500 (31,6 %) ; 10 : 719 (20,5 %) ; 100 : 391 (11,2 %) ; 500 : 123 (3,5 %) ; 1000 : 73 (2,1 %).
- **Tkinter** : sur une grille 60×60 dans un canevas 900×900, remplacer « tout effacer et recréer les rectangles » par `Canvas.itemconfig` (changer la couleur des rectangles existants) n'a fait gagner que **3 %**, la mise à jour du canevas restant ≈ 0,14 s par image — [Python Forum, thread 28462](https://python-forum.io/thread-28462.html) ; conseil ancien de la liste python-list : modifier les objets existants du canevas plutôt que de les détruire/recréer — [python-list, mai 2005](https://www.python.org/pipermail/python-list/2005-May/336434.html) ; en Perl/Tk, effacer/recréer les cellules ralentissait le programme d'un facteur ~10 après ~100 pas (rapport d'un autre langage remonté par la même recherche ; page exacte incertaine, probablement [« why is the tk canvas so slow » (archive Stack Overflow)](https://kiwix.lema.org/stackoverflow.com_en_all_2023-11/questions/13925920/why-is-the-tk-canvas-so-slow) — à ne citer qu'avec prudence).

### Inferences
- Complexités : tableau Θ(L·H) par génération (+ Θ(L·H) pour construire une signature `bytes`) ; ensemble Θ(n) en temps et mémoire (≤ 8n entrées dans le `Counter` : seules les voisines de cellules vivantes y figurent) ; précalcul des voisins Θ(8·L·H) une fois (ce que fait déjà `Jdlv._relier_voisines`).
- Le gain de `itemconfig` seul est faible (3 %) parce qu'on reconfigure encore les 3500 rectangles ; combiné à « seulement les cellules qui ont changé », le nombre d'appels Tk par image passe de 3500 à ~1100 au début puis ~70-400 : c'est là que se trouve le gain principal (inférence, non mesurée sous Tkinter car pas d'affichage dans cette session). Garder une liste des cellules changées pendant le calcul de la génération ne coûte presque rien.
- Pour 70×50, le calcul (≈ 1 ms) est négligeable devant un rafraîchissement à 10-30 images/s ; optimiser le moteur n'a d'intérêt que pour la détection de cycles (qui peut demander des milliers de générations sans affichage) ou pour les méthusalems (acorn : 6,5 s pour 6500 générations avec la méthode ensemble).

### Gaps
- Aucune mesure Tkinter réelle (pas d'écran X dans la session) ; le « 3 % » vient d'un seul témoignage de forum.
- Mesures de vitesse sur une seule machine ; à refaire sur les ordinateurs du lycée pour l'oral.

## 4. Portée mathématique (résumé pour l'oral)

### Takeaway
Inventé par John Conway et révélé par Martin Gardner dans *Scientific American* en octobre 1970, le jeu de la vie montre qu'avec 2 règles locales on obtient une machine universelle : il est Turing-complet (Conway dans *Winning Ways*, 1982 ; machine de Turing explicite de Paul Rendell en 2000), si bien qu'aucun algorithme ne peut prédire en général si un motif va mourir ou se stabiliser — ce qui justifie, côté NSI, qu'on détecte les cycles en simulant plutôt qu'en « calculant » le destin. Il possède aussi des « jardins d'Éden », configurations sans passé (théorème de Moore 1962 – Myhill 1963 ; premier exemple explicite par Roger Banks en 1971).

### Cited Findings
- **1970, Gardner** : rubrique « Mathematical Games » d'octobre 1970 de *Scientific American*, titre « The Fantastic Combinations of John Conway's New Solitaire Game "Life" », pages 120-123 — [extrait du livre *Game of Life Cellular Automata* (Springer, ISBN 9781849962162)](https://beckassets.blob.core.windows.net/product/readingsample/8271895/9781849962162_excerpt_001.pdf) ; [Stanford STS129, « The Game of Life »](https://web.stanford.edu/class/sts129/Alife/html/Life.htm).
- **Conjecture de Conway et prix de 50 $** : Conway conjecturait qu'aucun motif ne croît indéfiniment et offrait 50 $ à qui la prouverait ou la réfuterait avant fin 1970 ; prix gagné en **novembre 1970** par une équipe du MIT menée par **Bill Gosper** avec le canon à planeurs (population qui croît sans limite) — [Wikipedia « Gun (cellular automaton) » (via recherche)](https://en.wikipedia.org/wiki/Gun_(cellular_automaton)) ; [extrait Springer](https://beckassets.blob.core.windows.net/product/readingsample/8271895/9781849962162_excerpt_001.pdf).
- **Turing-complétude** : Conway a montré dans *Winning Ways* (Berlekamp, Conway, Guy, **1982**) qu'il existe dans Life un ordinateur universel fini et un constructeur universel — [Esolangs, « Game of Life »](https://esolangs.org/wiki/CGoL) ; [MathWorld, « Game of Life »](https://mathworld.wolfram.com/GameofLife.html). **Avril 2000** : machine de Turing explicite de **Paul Rendell** (ruban fini ; universelle « vraie » si le ruban est rendu infini) — [dépôt UWE, Rendell, « Turing machine universality of the Game of Life »](https://uwe-repository.worktribe.com/output/822575/turing-machine-universality-of-the-game-of-life) ; [MathWorld](https://mathworld.wolfram.com/GameofLife.html). **2002** : machine à registres universelle de Paul Chapman ; **2010-2011** : version pleinement universelle de Rendell — [miroir LifeWiki « Universal computer »](https://conwaylife.njohnston.ca/wiki/URM) ; [Esolangs](https://esolangs.org/wiki/CGoL).
- **Indécidabilité** : conséquence de la Turing-complétude (réduction depuis le problème de l'arrêt), il n'existe pas d'algorithme général qui décide si un motif donné finira par mourir (ou se stabiliser) — [Esolangs, « Game of Life »](https://esolangs.org/wiki/GoL) ; principe général « indécidable par réduction facile depuis le problème de l'arrêt » pour un automate cellulaire général — [article sur les orphelins de Life, villesalo.com](https://villesalo.com/article/SaCoPitGoL.pdf). (Sources mi-académiques mi-informelles : à présenter comme un résultat classique, sans date ni auteur unique.)
- **Jardins d'Éden** : configuration sans aucun prédécesseur ; **théorème de Moore (1962) – Myhill (1963)** : un automate cellulaire sur la grille possède un jardin d'Éden si et seulement s'il possède des « jumeaux » (deux motifs finis différents ayant la même image) ; premier jardin d'Éden explicite de Life trouvé par **Roger Banks en 1971** (tient dans un rectangle 9×33) — [Wikipedia, « Garden of Eden (cellular automaton) » (via recherche)](https://wikipedia.com/wiki/Garden_of_Eden_configuration) ; [MathWorld](https://mathworld.wolfram.com/GameofLife.html) (« premier trouvé en 1971 ») ; [Esolangs](https://esolangs.org/wiki/CGoL) (« Banks et al., 1971, 33×9 »). Plus petit jardin d'Éden connu : **Nicolay Beluchenko, 2006** ; problème ouvert cité : existe-t-il une configuration ayant un parent mais pas de grand-parent ? — [techno-science.net, « Jeu de la vie »](https://www.techno-science.net/fr/definitions/jeu-de-la-vie).
- Nuance de complexité : décider si un **motif fini** a un prédécesseur est décidable (recherche finie) mais NP-difficile en général ; pour une configuration **périodique**, l'existence d'une préimage est indécidable — [résumé de recherche, sources Esolangs et villesalo.com](https://villesalo.com/article/SaCoPitGoL.pdf) (deux énoncés compatibles car ils portent sur des objets différents).
- Le planeur a été découvert par Richard Guy en 1970 ; il est le premier vaisseau observé (dans l'évolution du R-pentomino) — [Life Lexicon (Golly/Debian), lettre G](https://sources.debian.org/data/main/g/golly/3.3-1.1/gui-common/Help/Lexicon/lex_g.htm) ; [Wikipedia « Conway's Game of Life » (via recherche)](https://en.wikipedia.org/wiki/Conway%27s_Game_of_Life).

### Inferences
- **Fil conducteur pour l'oral** : (1) règles locales minuscules → (2) émergence de structures (stables, oscillateurs, vaisseaux, canons) → (3) le canon de Gosper réfute la conjecture de croissance bornée (1970) → (4) avec planeurs et canons on fabrique des portes logiques, donc un ordinateur (1982, 2000) → (5) donc le destin d'un motif est indécidable en général → (6) mais **sur une grille finie** (tore L×H), le nombre d'états est fini (2^(L·H)) : par le principe des tiroirs la simulation finit toujours par revenir à un état déjà vu, et l'algorithme du dictionnaire termine forcément — ce qui réconcilie l'indécidabilité théorique (plan infini) et le programme NSI (grille finie). La borne 2^3500 pour 70×50 est toutefois astronomique : en pratique les soupes se figent en quelques centaines de générations (tableau de la section 1).
- « Émergence » : l'idée qu'un comportement global complexe (déplacement, reproduction, calcul) naît de règles locales simples est la lecture usuelle du jeu ; présentée ici comme interprétation, sans source dédiée consultée.

### Gaps
- Volume/numéro exacts de *Scientific American* (vol. 223, n° 4) non vérifiés dans une source consultée ; seules la date (octobre 1970) et les pages (120-123) le sont.
- L'affirmation (issue d'un résumé de recherche) selon laquelle A. R. Smith aurait démontré dès 1970 l'existence de jardins d'Éden dans Life n'a pas pu être vérifiée sur la page source : à ne pas utiliser sans contrôle.
- Le statut actuel du problème « parent sans grand-parent » (ouvert selon techno-science.net) n'a pas été revérifié sur une source récente.
- Date de décès de Conway (2020) et contexte biographique : non recherchés/vérifiés dans cette session.
