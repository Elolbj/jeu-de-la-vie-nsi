# Variantes de règles et extensions originales du Jeu de la vie (projet Terminale NSI, Python + Tkinter)

> **Note de méthode (à lire en premier).** Depuis cette session, les sites conwaylife.com (LifeWiki), en.wikipedia.org et golly.sourceforge.io n'étaient **pas joignables** (hôtes hors de la liste réseau autorisée). J'ai donc travaillé ainsi :
> 1. **Source primaire hors-ligne** : la documentation officielle de Golly 3.3 (pages d'aide HTML, Life Lexicon, fichiers de motifs `.rle`, fichiers `.rule`), lue depuis le paquet Ubuntu `golly 3.3-1.1build3`, qui contient exactement les pages publiées sur golly.sourceforge.io/Help/. Je cite les URL en ligne correspondantes. Ces faits sont **vérifiés mot pour mot**.
> 2. **Résumés de moteur de recherche** (WebSearch) des pages LifeWiki / Wikipédia. Ils sont fiables pour les chaînes de règles, mais **les citations ne sont pas vérifiées mot pour mot** : elles sont signalées « (via résumé de recherche) ».
> 3. **Simulations locales** en Python pur (grille 70×50, sans numpy), que j'ai écrites pour vérifier certains comportements et mesurer les performances. Elles sont rangées dans les sections « Inferences », avec la mention « simulation locale ».

## 1. Variantes de règles en notation B/S (automates « Life-like ») : chaînes exactes, comportements, intérêt visuel sur ~70×50

### Takeaway
Une seule fonction `prochaine_generation(grille, B, S)` paramétrée par deux ensembles d'entiers suffit à couvrir les 2^18 = 262 144 règles « Life-like ». Ajouter un champ de saisie « B36/S23 » ou un menu de règles prédéfinies est donc l'originalité au meilleur rapport effort/effet. Sur une petite grille torique de 70×50, les règles les plus « vivantes » sont Conway, HighLife, Day & Night, Diamoeba, 2x2, Seeds, Replicator et Coral. Maze et Life without death se figent en quelques générations si on part d'une soupe dense.

### Cited Findings
**Notation**
- Notation B/S de Golly (verbatim) : « Such rules are defined using "B0...8/S0...8" notation, where the digits after B specify the counts of live neighbors necessary for a cell to be born in the next generation, and the digits after S specify the counts of live neighbors necessary for a cell to survive to the next generation. » — [Golly Help: QuickLife](https://golly.sourceforge.io/Help/Algorithms/QuickLife.html)
- Il existe 2^18 = 262 144 combinaisons de conditions de naissance et de survie possibles, dont seule une petite fraction a été étudiée en détail (via résumé de recherche). — [Wikipedia EN : Life-like cellular automaton](https://en.wikipedia.org/wiki/Life-like_cellular_automaton)
- Une ancienne notation, S/B (survie/naissance, par ex. `23/3` pour Life), existe encore : la ligne `#r` des fichiers RLE produits par XLife donne la règle « in survival/birth form, such as 23/3 for Life » (via résumé de recherche). — [LifeWiki : RLE](https://conwaylife.com/wiki/RLE)
- Golly accepte aussi le voisinage de von Neumann (suffixe `V`, comptes de 0 à 4, exemples `B13/S012V`, `B2/S013V`) et un voisinage hexagonal émulé sur grille carrée (suffixe `H`, comptes de 0 à 6). Ce dernier ignore les coins NE et SO du voisinage de Moore. Exemple donné : `x = 7, y = 6, rule = B245/S3H` / `obo$4bo$2bo$bo2bobo$3bo$5bo!`. — [Golly Help: QuickLife](https://golly.sourceforge.io/Help/Algorithms/QuickLife.html)

**Règles demandées (chaîne exacte → comportement)**
- `B3/S23` **Life (Conway)** : « John Conway's rule is by far the best known and most explored CA. » — [Golly Help: QuickLife](https://golly.sourceforge.io/Help/Algorithms/QuickLife.html)
- `B36/S23` **HighLife** : « Very similar to Conway's Life but with an interesting replicator. » — [Golly Help: QuickLife](https://golly.sourceforge.io/Help/Algorithms/QuickLife.html)
  - Le réplicateur de HighLife est « de loin le plus connu » des réplicateurs Life-like. Il reste confiné sur une ligne diagonale. On compte 2^n copies à la génération 12(2^n − 1), avec des centres espacés de 4 cellules ; les deux extrémités de la ligne avancent à c/6. Il est si petit qu'il apparaît souvent spontanément à partir d'une soupe aléatoire (via résumé de recherche). — [LifeWiki : OCA:HighLife/Replicator (miroir)](https://conwaylife.njohnston.ca/wiki/OCA:HighLife/Replicator)
  - Découvert par Nathan Thompson en 1994. HighLife est décrit comme la première règle intéressante où l'on a trouvé un réplicateur (via résumé de recherche). — [Eppstein : Replicators B36/S23](https://ics.uci.edu/~eppstein/ca/replicators/b36s23.html)
  - Le « bomber » (réplicateur + clignotant) est un vaisseau diagonal de période 48 qui avance à c/6 (via résumé de recherche). — [Wikipedia EN : Highlife](https://en.wikipedia.org/wiki/Highlife_(cellular_automaton))
- `B2/S` **Seeds** : « Every living cell dies every generation, but most patterns still explode. » — [Golly Help: QuickLife](https://golly.sourceforge.io/Help/Algorithms/QuickLife.html)
  - Étudiée d'abord par Brian Silverman et nommée par Mirek Wójtowicz. Tous les motifs de Seeds sont des « phoenix » (toutes les cellules vivantes s'éteignent à chaque pas). La plupart des motifs dégénèrent en un chaos qui envahit tout l'univers. Les vaisseaux connus vont surtout à c/1 (via résumé de recherche). — [Wikipedia EN : Seeds](https://en.wikipedia.org/wiki/Seeds_(cellular_automaton))
- `B3678/S34678` **Day & Night** : « Dead cells in a sea of live cells behave the same as live cells in a sea of dead cells. » — [Golly Help: QuickLife](https://golly.sourceforge.io/Help/Algorithms/QuickLife.html)
  - Inventée et nommée en 1997 par Nathan Thompson, puis étudiée par David I. Bell. Partant d'une soupe aléatoire, la grille se divise en grandes zones « jour » et « nuit » qui grossissent (via résumé de recherche). — [Wikipedia EN : Day and Night](https://en.wikipedia.org/wiki/Day_and_Night_(cellular_automaton))
  - C'est la règle « auto-complémentaire » la plus connue (via résumé de recherche). — [LifeWiki : Self-complementary (miroir)](https://conwaylife.njohnston.ca/wiki/Self-complementary)
  - Le fichier d'exemple Golly `Day-and-Night-gun-and-antigun.rle` (David Bell, 2009) illustre cette symétrie. Il montre aussi qu'un signal peut traverser la frontière entre zones jour et nuit. — [Golly (motifs fournis)](https://golly.sourceforge.io/)
- `B1357/S1357` **Replicator (Fredkin)** : le fichier Golly `Patterns/Life-Like/replicator.rle` porte le commentaire `#C All patterns in this rule replicate.` — [Golly (motifs fournis)](https://golly.sourceforge.io/)
  - Une cellule naît ou survit si elle a un nombre impair de voisins ; tout motif finit remplacé par plusieurs copies de lui-même (via résumé de recherche). — [Wikipedia EN : Life-like cellular automaton](https://en.wikipedia.org/wiki/Life-like_cellular_automaton)
- `B3/S12345` **Maze** : une soupe aléatoire évolue en structures labyrinthiques complexes, avec des murs bien définis qui bordent des couloirs (via résumé de recherche). — [LifeWiki : OCA:Maze (miroir)](https://conwaylife.njohnston.ca/wiki/OCA:Maze)
- `B34/S34` **34 Life** : longtemps prise pour une alternative stable à Life, jusqu'à ce que des simulations montrent que les grands motifs ont tendance à exploser (via résumé de recherche). — [Wikipedia EN : Life-like cellular automaton](https://en.wikipedia.org/wiki/Life-like_cellular_automaton)
- `B3/S012345678` **Life without death** : une cellule devenue vivante ne meurt jamais. La règle est aussi appelée « Inkspot » ou « Flakes » (via résumé de recherche). — [Wikipedia EN : Life-like cellular automaton](https://en.wikipedia.org/wiki/Life-like_cellular_automaton)
- `B35678/S5678` **Diamoeba** : « Creates diamond-shaped blobs with unpredictable behavior. » — [Golly Help: QuickLife](https://golly.sourceforge.io/Help/Algorithms/QuickLife.html) ; règle confirmée par [LifeWiki : OCA:Diamoeba (miroir)](https://conwaylife.njohnston.ca/wiki/OCA:Diamoeba)
- `B368/S245` **Morley** (aussi appelée « Move ») : nommée d'après Stephen Morley (via résumé de recherche). — [Wikipedia EN : Life-like cellular automaton](https://en.wikipedia.org/wiki/Life-like_cellular_automaton). Golly fournit un dossier `Patterns/Life-Like/Morley` qui contient `breeder2.rle`, `enterprise-gun.rle` et `growing-ship.rle` : la règle possède donc des canons et des « breeders ». — [Golly (motifs fournis)](https://golly.sourceforge.io/)
- `B36/S125` **2x2** : son nom vient de ce qu'elle émule un automate plus simple qui agit sur des blocs de 2×2 cellules. — [Nathaniel Johnston : The B36/S125 "2×2" Life-like CA](https://njohnston.ca/?p=993)

**Autres règles faciles et spectaculaires (bonus)**
- `B234/S` **Serviettes / Persian Rug** : « A single 2x2 block turns into a set of Persian rugs. » ; `B345/S5` **LongLife** : « Oscillators with extremely long periods can occur quite naturally. » — [Golly Help: QuickLife](https://golly.sourceforge.io/Help/Algorithms/QuickLife.html)
- `B3/S45678` **Coral** : `#C "Coral": this rule produces patterns with a surprisingly slow rate of expansion and an interesting coral-like texture.` (fichier `coral.rle`, issu de MCell, auteur de la règle inconnu) ; `B345/S5` « White Whale », un oscillateur de période 160 000 346 (fichier `white-whale.rle`) ; `B25678/S5678:T20,20` « ice-nine » sur un tore de 20×20 (fichier `ice-nine.rle`). — [Golly (motifs fournis)](https://golly.sourceforge.io/)

### Inferences
- **Implémentation** : ranger la règle sous la forme `B = {3, 6}` et `S = {2, 3}`. Le cœur de l'algorithme devient alors `vivant_suivant = (n in S) if vivant else (n in B)`. Pour analyser la chaîne saisie, une expression régulière insensible à la casse suffit, par exemple `^B([0-8]*)/S([0-8]*)$`. On peut accepter en plus l'ancienne forme S/B `^([0-8]*)/([0-8]*)$` (ordre inversé !).
- **Performances (simulation locale)** : en Python pur, avec une grille aplatie (liste de 3 500 entiers) et la **liste des 8 voisins précalculée** pour chaque cellule, 13 règles × 300 générations sur un tore de 70×50 ont pris 6,9 s, soit **≈ 1,8 ms par génération** sur la machine de test. Le calcul n'est donc pas le facteur limitant. Dans Tkinter, c'est le dessin qui coûtera le plus. Une piste standard (non sourcée) : créer les rectangles une seule fois, puis appeler `itemconfig` seulement sur les cellules qui changent.
- **Intérêt visuel sur 70×50 (simulation locale, soupe aléatoire, graine fixe, densité 30 %, ou 50 % pour Day & Night et Diamoeba, tore)**. Populations aux générations 0 / 10 / 50 / 100 / 200 / 300 :
  - Conway 1055/770/406/316/214/238 : toujours actif à la génération 300 ;
  - HighLife 1055/869/483/442/213/96 : toujours actif ;
  - Seeds 1055/780/743/715/762/743 : chaos permanent, environ 21 % de la grille ;
  - Day & Night 1721/1581/1458/1395/1049/1031 : toujours actif, des zones se forment ;
  - Replicator ≈ 1750 en permanence : texture chaotique ;
  - Maze : figée en cycle de période 2 dès la génération 12 ;
  - 34 Life ≈ 1480 : actif ;
  - Life without death : figée dès la génération 8 (2 364 cellules) ;
  - Diamoeba 1721 → 1927 : blobs mouvants ;
  - Morley 1055 → 28 : cycle de période 4 à partir de la génération 141, il ne reste que quelques objets ;
  - 2x2 1055 → 434 : actif ;
  - Coral 1055 → 42 (gén. 10) → 1772 (gén. 300) : croissance lente et régulière, très visuelle ;
  - Serviettes ≈ 1300 : actif.
  - **Conclusion** : pour Maze et Life without death, partir d'un **petit motif dessiné à la main**, ou d'une soupe à faible densité, plutôt que d'une soupe dense. Pour HighLife, prévoir un bouton « placer un réplicateur ». Ce test ne porte que sur une seule graine : il est indicatif, pas statistique.
- Le voisinage hexagonal façon Golly (ignorer les voisins NE et SO) ou celui de von Neumann (4 voisins) sont des originalités peu coûteuses : il suffit de changer la liste des décalages `(dx, dy)`.

### Gaps
- Le tableau complet des règles de LifeWiki et de Wikipédia (descriptions exactes, mot pour mot) n'a pas pu être consulté directement : les hôtes étaient inaccessibles. Les descriptions de 34 Life, Life without death, Maze, Morley et Replicator proviennent de résumés de recherche.
- Mazectric (`B3/S1234`), Anneal, Amoeba, Gnarl, etc. ne sont pas vérifiés ici.
- La page Wikipédia FR « Jeu de la vie » n'a pas été consultée (hôte inaccessible).

## 2. Variantes multi-états et multicolores : Brian's Brain, Immigration, QuadLife (couleur des nouveau-nés)

### Takeaway
Les trois variantes sont implémentables en ajoutant un entier « état » ou « couleur » par cellule. Dans Brian's Brain, une cellule vivante passe toujours par un état « mourant » qui ne compte pas comme voisin. Dans Immigration (2 couleurs) et QuadLife (4 couleurs), un nouveau-né a exactement 3 parents (naissance B3) et prend la couleur majoritaire. Dans QuadLife, si les 3 parents sont tous de couleurs différentes, il prend la 4e couleur. Les survivants gardent leur couleur.

### Cited Findings
- **Immigration** (verbatim) : « A form of colourised Life in which there are two types of ON cell, a newly-born cell taking the type of the majority of its three parent cells and surviving cells remaining of the same type as in the previous generation. » — [Life Lexicon, entrée « Immigration » (copie fournie avec Golly 3.3)](https://sources.debian.org/data/main/g/golly/3.3-1.1/gui-common/Help/Lexicon/lex_i.htm)
- **QuadLife** (verbatim) : « A form of colourised Life in which there are four types of ON cell. A newly-born cell takes the type of the majority of its three parent cells, or the remaining type if its parent cells are all of different types. In areas where there are only two types of ON cell QuadLife reduces to Immigration. » — [Life Lexicon, entrée « QuadLife »](https://sources.debian.org/data/main/g/golly/3.3-1.1/gui-common/Help/Lexicon/lex_q.htm)
- **Brian's Brain** : 3 états (allumé, mourant, éteint). Une cellule éteinte s'allume si exactement 2 de ses 8 voisins de Moore sont allumés, comme dans la règle de naissance de Seeds. Toute cellule allumée passe à « mourant ». L'état mourant ne compte pas comme voisin allumé et empêche toute naissance à cet endroit. Presque tous les motifs sont des vaisseaux. Il existe des oscillateurs, par exemple un oscillateur de période 3 à 4 cellules allumées et 4 mourantes. La règle est due à Brian Silverman (via résumé de recherche). — [Wikipedia EN : Brian's Brain](https://en.wikipedia.org/wiki/Brian%27s_Brain)
- Le modèle NetLogo nomme les états *firing* (blanc), *refractory* (rouge) et *dead* (noir) : une cellule *firing* devient toujours *refractory* au pas suivant, et une *refractory* meurt toujours au pas suivant (via résumé de recherche). — [NetLogo : Brian's Brain](https://ccl.northwestern.edu/netlogo/models/Brian%27sBrain)
- **Famille « Generations » de Golly** : il s'agit de règles « similar to Life but with an extra history component that allows cells to have up to 256 states ». La notation est `survie/naissance/n`, où n est le nombre total d'états (de 2 à 256). Brian's Brain s'y écrit `/2/3`. Autres exemples cités verbatim : `345/2/4` Star Wars, `2367/3457/5` Banners, `234/34678/24` Bloomerang, `124567/378/4` Caterpillars, `23/2/8` Cooties, `2/13/21` Fireworks, `12/34/3` Frogs, `12345/45678/8` Lava, `012345/458/3` Lines, `3456/2/6` Sticks, `345/26/5` Transers, `1456/2356/16` Xtasy. — [Golly Help: Generations](https://golly.sourceforge.io/Help/Algorithms/Generations.html)
- Golly fournit la règle `BriansBrain.rule` (3 états) et la règle `LifeHistory` (7 états), où « state 2: history/envelope (state=2 if cell was ever ON) ». — [Golly (dossier Rules)](https://golly.sourceforge.io/)

### Inferences
- **Algorithme pour Immigration et QuadLife** : on compte les voisins vivants `n` sans tenir compte de la couleur, et on applique B3/S23 normalement. Pour une naissance (n = 3), on récupère les couleurs des 3 voisins vivants ; si une couleur apparaît au moins 2 fois, on la prend. Dans QuadLife, si les trois couleurs sont distinctes, on prend `({1,2,3,4} - {c1,c2,c3}).pop()`. Avec 2 couleurs et 3 parents, il y a toujours une majorité, donc aucun cas d'égalité n'est à gérer. On peut aussi appliquer la règle de majorité à HighLife, mais la naissance à 6 voisins fait alors apparaître des égalités 3–3 dans Immigration. Il faudrait une règle de départage à inventer et à documenter : c'est une vraie originalité, **non trouvée dans les sources**.
- **Brian's Brain** : états 0 (éteint), 1 (allumé), 2 (mourant). Transition : `1 → 2`, `2 → 0`, et `0 → 1` si exactement 2 voisins valent 1. Seuls les voisins à 1 comptent. La famille Generations `S/B/n` se généralise ainsi : une cellule vivante (état 1) qui ne satisfait pas S passe à 2, puis 3, …, jusqu'à n−1, puis 0. Seul l'état 1 compte comme voisin et une naissance n'est possible que sur une cellule à 0. Cette généralisation correspond à Brian's Brain (`/2/3`) d'après la description ci-dessus ; la sémantique exacte de MCell et LifeWiki n'a pas été relue.
- Idée de jeu : Immigration à 2 joueurs (rouge contre bleu). Chaque joueur place N cellules, puis on compte les cellules de chaque couleur après K générations.

### Gaps
- Les pages LifeWiki Immigration, QuadLife et Brian's Brain (chaînes de règle « officielles », par ex. une éventuelle notation `B2/S/C3` pour Brian's Brain) n'ont pas pu être consultées. Golly 3.3 ne fournit **ni règle Immigration ni règle QuadLife**. Leur prise en charge dans des versions plus récentes de Golly n'a pas été vérifiée.

## 3. Extensions visuelles : coloration par âge, traînées / « heat map », courbe de population

### Takeaway
Les trois extensions reposent sur un tableau parallèle à la grille (âge ou « chaleur ») et sur un second `Canvas` Tkinter pour la courbe de population. Golly lui-même propose une variante « historique » : un état qui marque toute cellule ayant déjà été vivante. C'est l'équivalent exact d'une traînée permanente.

### Cited Findings
- La règle `LifeHistory` de Golly ajoute un état « history/envelope (state=2 if cell was ever ON) » : toute cellule qui a été vivante au moins une fois reste marquée. Les fichiers d'exemple de Golly sur les grilles bornées l'utilisent (`rule = LifeHistory:T31,20`) pour visualiser le trajet d'un planeur. — [Golly (Rules/LifeHistory.rule, Patterns/Life/Bounded-Grids/torus.rle)](https://golly.sourceforge.io/Help/bounded.html)
- Des simulateurs en ligne proposent un thème « Heatmap » : les cellules nouvelles en bleu, les cellules anciennes qui virent au rouge (via résumé de recherche). — [toolv.com : Conway's Game of Life](https://toolv.com/en/app/conways-game-of-life)
- Un projet GitHub colore en rouge les cellules les plus jeunes, puis vers le bleu, et en violet les plus vieilles (via résumé de recherche). — [GitHub agohorel/game-of-life](https://github.com/agohorel/game-of-life)
- Un paquet Python pour terminal fait cycler 5 couleurs selon l'âge (cyan → vert → jaune → magenta → bleu) (via résumé de recherche). — [PyPI : game-of-life-tui](https://pypi.org/project/game-of-life-tui/)
- La technique classique de la « heat map » : une valeur de chaleur mise au maximum sur les cellules vivantes, puis diminuée d'un pas d'atténuation quand la cellule meurt, ce qui produit des traînées (via résumé de recherche, sources secondaires non nommées précisément).

### Inferences
- **Âge** : `age[i] = age[i] + 1` si la cellule survit, `1` si elle naît, `0` si elle est morte. Couleur : `palette[min(age, len(palette) - 1)]`, par exemple 10 à 20 nuances précalculées en `"#rrggbb"`. Un nouveau-né clair et une cellule ancienne foncée permettent de distinguer d'un coup d'œil les structures stables des fronts de croissance.
- **Traînée / heat map** : `chaleur[i] = 1.0` si vivante, sinon `chaleur[i] *= 0.85` (ou `-= 0.1`). On ne dessine que si `chaleur > seuil`. La variante « enveloppe » (LifeHistory) est un booléen `deja_vivante[i]`.
- **Courbe de population** : on stocke `historique.append(sum(grille))` à chaque génération et on trace sur un second `Canvas` avec `create_line(*points)` (liste aplatie de coordonnées). On redessine toutes les N générations, ou on garde une fenêtre glissante des 200 dernières valeurs.
- **Détecteur de stabilisation (simulation locale)** : on mémorise `bytes(grille)` dans un dictionnaire `{état: génération}`. Si un état revient, l'automate est entré dans un cycle de période `t - dict[état]`. Ce test m'a servi à détecter que Maze se fige en période 2 et Morley en période 4. C'est une fonctionnalité simple et originale : afficher « stabilisé à la génération X, période P ».

### Gaps
- Aucune source primaire (LifeWiki, Golly) ne définit une palette standard de coloration par âge : il s'agit d'une convention propre à chaque simulateur. LifeViewer (le visualiseur de LifeWiki) aurait des thèmes « avec historique », mais ses fonctionnalités n'ont pas pu être vérifiées.

## 4. Topologies : grille bornée, tore, bouteille de Klein ; effet sur les planeurs

### Takeaway
Une grille bornée (cellules extérieures mortes), un tore (`(x + dx) % W`) et une bouteille de Klein (un bord inversé) ne diffèrent que par la façon de calculer l'indice du voisin. C'est une option de menu facile et pédagogique. Sur un plan borné, le planeur s'écrase en bloc. Sur un tore, il revient périodiquement. Sur une bouteille de Klein, il revient « en miroir » après un passage, et à l'identique après deux.

### Cited Findings
- **Syntaxe Golly des grilles bornées** (suffixe ajouté à la règle) : `:P30,20` plan de 30×20 ; `:P30,0` hauteur infinie ; `:T0,20` tube ; `:T30,20` tore ; `:T30+5,20` tore avec décalage de +5 sur les bords horizontaux ; `:T30,20-2` décalage de −2 sur les bords verticaux ; `:K30*,20` bouteille de Klein avec les bords horizontaux tordus ; `:K30,20*` bords verticaux tordus ; `:K30*+1,20` Klein avec décalage ; `:C30,20` surface croisée (les deux paires de bords tordues, c'est-à-dire un plan projectif) ; `:S30` sphère (largeur = hauteur obligatoirement). Exemple : « B3/S23:T30,20 creates a toroidal Life universe 30 cells wide and 20 cells high. » — [Golly Help: Bounded Grids](https://golly.sourceforge.io/Help/bounded.html)
- **Plan** : « Golly ensures that all the cells neighboring the edges are set to state 0 before applying the transition rules ». **Tore** : « Golly copies the states of edge cells into appropriate neighboring cells outside the grid. » **Klein** : « If one pair of opposite edges are twisted 180 degrees (ie. reversed) before being joined then the result is a Klein bottle. » Pour `:K4*,3`, la rangée fantôme au-dessus de `A B C D` contient `L K J I` : c'est la dernière ligne lue à l'envers. Pour la surface croisée, « the corner cells have themselves as one of their neighbors ». — [Golly Help: Bounded Grids](https://golly.sourceforge.io/Help/bounded.html)
- **Sphère** : par convention, le bord haut est joint au bord gauche et le bord droit au bord bas. Les « pôles » n'ont pas le même voisinage que les deux autres coins. — [Golly Help: Bounded Grids](https://golly.sourceforge.io/Help/bounded.html)
- Le commentaire du fichier Golly `torus.rle` : « If the edge lengths are relatively prime, as in this example, then a glider will eventually visit every cell. » (règle `LifeHistory:T31,20`). — [Golly (Patterns/Life/Bounded-Grids/torus.rle)](https://golly.sourceforge.io/Help/bounded.html)
- Le Life Lexicon : sur un tore, « Every object in a torus universe obviously either dies or becomes a still life or oscillator. » Pour la bouteille de Klein : « use an m x n rectangle with the top edge joined to the bottom edge (as for a torus) and the left edge twisted and joined to the right. » — [Life Lexicon, entrées « torus » et « Klein bottle »](https://sources.debian.org/data/main/g/golly/3.3-1.1/gui-common/Help/Lexicon/lex_t.htm)
- Golly fournit des exemples pour chaque topologie (`torus.rle`, `torus-with-shift.rle`, `Klein-bottle.rle` avec la règle `LifeHistory:K40*,20`, `cross-surface.rle`, `sphere.rle`, `pulsars-in-tube.rle`). — [Golly Help: Bounded Grids](https://golly.sourceforge.io/Help/bounded.html)

### Inferences
- **Formules pour un voisin `(x + dx, y + dy)`** :
  - plan : ignorer le voisin s'il sort de `[0, W[ × [0, H[` ;
  - tore : `xx % W`, `yy % H` ;
  - Klein façon `:K W*,H` (bords haut et bas tordus) : si `yy` sort de la grille, on fait `yy %= H` puis `xx = W - 1 - xx`, et enfin `xx %= W`. Ce calcul reproduit exactement le diagramme `:K4*,3` de Golly, coins compris.
- **Vérifications par simulation locale (B3/S23, grille 70×50, planeur parti du coin haut-gauche vers le bas-droite)** :
  - plan borné : après 400 générations, le planeur est devenu un **bloc 2×2** collé au bord bas (cellules (48–49, 48–49)) ;
  - tore : le planeur revient à sa position et à sa phase de départ après **1 400 générations**, soit 4 × ppcm(70, 50) = 4 × 350. 70 et 50 ne sont pas premiers entre eux (pgcd = 10), donc le planeur ne visite **pas** toutes les cellules. Pour une démo « le planeur visite toute la grille », il faut des dimensions premières entre elles, par exemple 71×50 ou 31×20 comme dans Golly ;
  - Klein (bords haut et bas tordus) : retour à l'identique après **2 800 générations**, le double du tore. Après chaque traversée du bord tordu, le planeur réapparaît en image miroir et part dans l'autre direction horizontale.
- Pour un projet NSI, la combinaison la plus parlante est un menu « Bords : murs / tore / Klein », accompagné d'un planeur ou d'un canon de Gosper pour montrer la différence. Sur un tore, le flux de planeurs d'un canon de Gosper revient percuter le canon lui-même : effet visuel garanti, mais non vérifié en simulation ici.

### Gaps
- La page LifeWiki « Torus » et les éventuelles analyses publiées sur le comportement des planeurs dans une bouteille de Klein n'ont pas été consultées. Les observations « miroir » et « période double » viennent uniquement de ma simulation.

## 5. Formats de fichiers de motifs : RLE et plaintext `.cells` ; où trouver des motifs ; licences

### Takeaway
Le RLE se lit et s'écrit en environ 40 lignes de Python. Il comprend une ligne d'en-tête `x = …, y = …, rule = …`, puis des jetons `<nombre><b|o|$>` terminés par `!`, et des commentaires `#`. Le format `.cells` est encore plus simple : `!` pour les commentaires, `.` pour une cellule morte, `O` pour une vivante. Golly (licence GPL) fournit des milliers de motifs `.rle`. Le Life Lexicon est sous CC BY-SA 3.0. La licence du contenu de LifeWiki n'a pas pu être vérifiée.

### Cited Findings
**RLE : spécification (Golly, verbatim sauf mention contraire)**
- Le format RLE a été créé par Dave Buckingham. Golly en utilise une version étendue (« Extended RLE »). Exemple du r-pentomino : `x = 3, y = 3, rule = B3/S23` puis `b2o$2o$bo!`. — [Golly Help: File Formats](https://golly.sourceforge.io/Help/formats.html)
- « RLE data is indicated by a file whose first non-comment line starts with "x". A comment line is either a blank line or a line beginning with "#". » En-tête : `x = width, y = height, rule = rule`. « Whitespace can be inserted at any point in this line except at the beginning or where it would split a token. » Golly ignore les dimensions au chargement, mais les utilise comme cadre lors d'un collage. — [Golly Help: File Formats](https://golly.sourceforge.io/Help/formats.html)
- « The data is ordered a row at a time from top to bottom, and each row is ordered left to right. A "$" represents the end of each row and an optional "!" represents the end of the pattern. For two-state rules, a "b" represents an off cell, and a "o" represents an on cell. » — [Golly Help: File Formats](https://golly.sourceforge.io/Help/formats.html)
- **Multi-états** : « a "." represents a zero state; states 1..24 are represented by "A".."X", states 25..48 by "pA".."pX", states 49..72 by "qA".."qX", and on up to states 241..255 represented by "yA".."yO". The pattern reader is flexible and will permit "b" and "." interchangeably and "o" and "A" interchangeably. » — [Golly Help: File Formats](https://golly.sourceforge.io/Help/formats.html)
- **Nombres de répétition** : « Any data value or row terminator can be immediately preceded with an integer indicating a repetition count. Thus, "3o" and "ooo" both represent a sequence of three on cells, and "5$" means finish the current row and insert four blank rows ». — [Golly Help: File Formats](https://golly.sourceforge.io/Help/formats.html)
- **Longueur de ligne** : « The pattern writer attempts to keep lines about 70 characters long … but the reader will accept much longer lines. » — [Golly Help: File Formats](https://golly.sourceforge.io/Help/formats.html). Une grammaire communautaire dit que les générateurs « SHOULD NOT » produire de lignes de plus de 70 caractères (via résumé de recherche). — [Forum conwaylife : RLE grammar](https://conwaylife.njohnston.ca/forums/viewtopic.php?p=72791)
- Les cellules mortes en fin de ligne n'ont pas besoin d'être encodées, pas plus que la fin de la dernière ligne. Exemple du planeur selon LifeWiki : `x = 3, y = 3` / `bo$2bo$3o!` (via résumé de recherche). — [LifeWiki : RLE](https://conwaylife.com/wiki/RLE)
- **Lignes `#`** (LifeWiki, via résumé de recherche) :
  - `#C` : commentaire ; `#c` : idem, déconseillé ;
  - `#N` : nom du motif ;
  - `#O` : auteur et date de création ;
  - `#R` : coordonnées du coin haut-gauche (XLife, souvent négatives pour centrer le motif) ;
  - `#P` : équivalent de `#R` (vient de Life32) ;
  - `#r` : règle en notation S/B, par ex. `23/3` (XLife). La méthode standard reste le champ `rule =` de l'en-tête.

  — [LifeWiki : RLE](https://conwaylife.com/wiki/RLE). On retrouve ces balises dans les fichiers Golly, par exemple `#N Switch engine ping-pong` / `#O Michael Simkin, 29 October 2014` / `#C …`. Sur l'ensemble des motifs fournis par Golly, on compte environ 4 187 lignes `#C`, 29 `#CXRLE`, 6 `#N`, 4 `#O` et 1 `#D` (comptage local). — [Golly (motifs fournis)](https://golly.sourceforge.io/)
- **`#CXRLE`** (Golly) : `#CXRLE Pos=0,-1377 Gen=3480106827776` donne la position du coin haut-gauche et le numéro de génération. Les autres lignes de commentaire situées en haut ou en bas du fichier s'affichent comme informations. — [Golly Help: File Formats](https://golly.sourceforge.io/Help/formats.html)
- **Champ `rule =`** : on trouve en pratique `B3/S23`, `B36/S23`, `B3678/S34678`, des règles Generations `345/3/6` ou `3458/37/4`, et des grilles bornées `B25678/S5678:T20,20` ou `LifeHistory:K40*,20` (fichiers Golly `Delta.rle`, `Sawfish.rle`, `ice-nine.rle`, `Klein-bottle.rle`). Dans les fichiers Golly, les répétitions de 2 s'écrivent aussi bien `2o` que `oo` (par ex. `87booboboo`). — [Golly (motifs fournis)](https://golly.sourceforge.io/)

**Plaintext `.cells`**
- Le format dessine le motif avec des caractères : `.` pour une cellule morte et `O` (o majuscule) pour une vivante. Les lignes qui commencent par `!` contiennent des métadonnées (`!Name: Glider`) ou des commentaires. Il n'y a pas de limite de longueur de ligne. Le format vient du programme « Game of Life » d'Edwin Martin et utilise l'extension `.cells`. Variantes : certains fichiers anciens omettent les cellules mortes en fin de ligne ou laissent vides les lignes entièrement mortes ; un fichier utilisait `*` à la place de `O`, par erreur (via résumé de recherche). — [LifeWiki : Plaintext (miroir)](https://conwaylife.njohnston.ca/wiki/Plaintext)

**Sources de motifs et licences**
- Golly est distribué sous **GNU GPL v2 ou ultérieure** (« Copyright (C) 2005-2019 The Golly Gang »). Il est livré avec un dossier `Patterns/` organisé par familles (`Life/` avec Guns, Spaceships, Oscillators, Methuselahs, Bounded-Grids… ; `Life-Like/` ; `Generations/` ; etc.). — [Golly : License](https://golly.sourceforge.io/) (fichier `License.html` du paquet)
- Le Life Lexicon (Stephen Silver 1997–2006, mis à jour par Dave Greene et David Bell en 2016–2018, Release 29 du 2 juillet 2018) : « may be freely copied, modified and distributed under the terms of the Creative Commons Attribution-ShareAlike 3.0 Unported licence (CC BY-SA 3.0), as long as due credit is given ». Il contient de nombreux motifs au format `.`/`O`. — [Life Lexicon (introduction)](https://sources.debian.org/data/main/g/golly/3.3-1.1/gui-common/Help/Lexicon/lex.htm)
- ConwayLife.com héberge LifeWiki et des forums de discussion (via résumé de recherche). — [Wikipedia EN : LifeWiki](https://en.wikipedia.org/wiki/LifeWiki)

### Inferences
- **Parseur RLE minimal** : ignorer les lignes vides et celles qui commencent par `#` (en conservant `#N` et `#C` pour l'affichage). Lire la ligne `x` avec une expression régulière `x\s*=\s*(\d+)\s*,\s*y\s*=\s*(\d+)(?:\s*,\s*rule\s*=\s*(\S+))?`. Concaténer ensuite toutes les lignes restantes jusqu'à `!`, puis parcourir les caractères avec un compteur `n` qui accumule les chiffres :
  - `b` ou `.` : avancer `x += n` ;
  - `o` ou `A` : poser `n` cellules vivantes ;
  - `$` : `y += n` et `x = 0` ;
  - `!` : arrêter ;
  - puis remettre `n = 1`.

  Ignorer les autres caractères (espaces, fins de ligne). Pour l'**écrivain**, faire l'inverse : regrouper les répétitions, ne pas écrire les `b` en fin de ligne, fusionner les `$` consécutifs (`3$`) et couper les lignes à 70 caractères maximum.
- Il est prudent d'ignorer tout ce qui suit `!`, même si la source primaire (Golly) dit seulement que `!` est « optional » et marque la fin du motif.
- Mise en garde pour une grille de 70×50 : beaucoup de motifs de Golly ou de LifeWiki sont bien plus grands (par ex. 588×601 pour le vaisseau à réplicateurs de HighLife). Le chargeur doit vérifier `x <= W` et `y <= H` et refuser le motif ou le recadrer.
- **Licence** : pour un projet scolaire non publié, inclure quelques fichiers `.rle` classiques (planeur, canon de Gosper, r-pentomino, réplicateur HighLife) en conservant leurs lignes `#C`, `#N` et `#O` et en citant la source (Golly GPL, Lexicon CC BY-SA) est la pratique la plus sûre. Ce n'est pas un avis juridique.

### Gaps
- **Licence du contenu de LifeWiki et des fichiers de motifs de conwaylife.com : non vérifiée** (la page « LifeWiki:Copyrights » était inaccessible et la recherche ne l'a pas fait remonter). À vérifier dans le pied de page de LifeWiki avant de redistribuer des fichiers.
- L'existence et l'URL exacte d'une archive de tous les motifs de LifeWiki (souvent citée comme `all.zip`) n'ont pas été vérifiées.
- Le texte exact de la page LifeWiki sur le contenu situé après `!` et sur la limite de 70 caractères n'a pas été relu directement.

## 6. Idées d'interaction vues dans les bons simulateurs (Golly, simulateurs en ligne)

### Takeaway
Golly propose undo/redo (y compris de la génération), Reset vers la génération de départ, une « timeline » enregistrable pour revenir en arrière, des réglages de vitesse (Faster/Slower), et le collage de motifs avec rotation, miroir et modes Copy/Or/Xor. Toutes ces fonctions se transposent en Tkinter avec une pile (`list`) d'états précédents et quelques raccourcis clavier.

### Cited Findings
- **Undo/Redo** : Undo « Lets you undo one or more recent changes, including all editing » ; Redo « Lets you redo one or more recently undone changes ». L'historique de redo est effacé dès qu'on fait un nouveau changement. Exemple donné : faire pivoter la sélection, annuler la rotation, puis éditer une cellule rend la rotation impossible à refaire. Chaque calque a son propre historique. — [Golly Help: Edit Menu](https://golly.sourceforge.io/Help/edit.html)
- **Reset** : « Restores the starting pattern and generation count. It also resets the algorithm, rule, scale, location, step size, selection and layer name to the values they had at the starting generation. » — [Golly Help: Control Menu](https://golly.sourceforge.io/Help/control.html)
- **Timeline (rembobinage)** : « Start/Stop Recording » enregistre en mémoire une suite de motifs séparés par le pas courant, jusqu'à 32 000 images au maximum. Tant qu'une timeline existe, l'édition et la génération sont désactivées. « Delete Timeline » fait de l'image affichée la génération courante, et les images suivantes sont perdues. — [Golly Help: Control Menu](https://golly.sourceforge.io/Help/control.html)
- **Pas à pas et vitesse** : « Next Generation » avance d'une génération. Control-espace n'avance que la sélection et Maj-espace tout ce qui est hors de la sélection. « Next Step » avance d'un pas affiché sous la forme `b^e`. « Faster » augmente l'exposant (« increases the speed by displaying fewer generations »), « Slower » le diminue. La base est réglable de 2 à 2 000 000 000. Le mode « Hyperspeed » augmente automatiquement l'exposant toutes les 64 étapes. — [Golly Help: Control Menu](https://golly.sourceforge.io/Help/control.html)
- **Collage et tampon de motifs** : après « Paste », on clique pour choisir l'emplacement. Pendant ce temps, les raccourcis de miroir et de rotation modifient le motif à coller. `M` fait défiler le mode de collage (« Copy, Or and Xor ») et `L` la position du curseur dans le rectangle (un coin ou le milieu). Golly peut aussi changer de règle si le motif collé en contient une (réglable dans les préférences). — [Golly Help: Edit Menu](https://golly.sourceforge.io/Help/edit.html)
- **Transformations** : « Flip Top-Bottom », « Flip Left-Right », « Rotate Clockwise » (« The current selection is rotated 90 degrees clockwise about its center. ») et « Rotate Anticlockwise ». — [Golly Help: Edit Menu](https://golly.sourceforge.io/Help/edit.html)

### Inferences
- **Retour arrière (step back)** : le Jeu de la vie n'est pas réversible : un état a en général plusieurs prédécesseurs, ou aucun. On ne peut donc pas « calculer » la génération précédente, il faut la **mémoriser**. Une pile `historique = []` bornée (`collections.deque(maxlen=500)`) de copies de la grille suffit. Sur une grille 70×50 stockée en `bytes`, cela fait 3 500 octets par état, donc environ 1,75 Mo pour 500 états. Le même mécanisme sert pour l'undo des éditions à la souris.
- **Tampon de motifs** : une bibliothèque de motifs stockés en listes de coordonnées `[(x, y), …]`, chargés depuis des `.rle`. Rotation de 90° : `(x, y) → (h - 1 - y, x)`. Miroir gauche-droite : `(x, y) → (w - 1 - x, y)`. Aperçu « fantôme » sous la souris avec `<Motion>`, pose au clic `<Button-1>`, rotation avec la touche `r`. Modes Copy/Or/Xor : Or ajoute les cellules, Xor inverse les cellules de la grille sous le motif, Copy écrase le rectangle.
- **Vitesse** : un `Scale` Tkinter qui règle le délai de `after(delai, boucle)`. On peut ajouter un mode « N générations par image », équivalent du `b^e` de Golly, pour aller vite sans redessiner à chaque génération.
- Autres idées tirées de ce qui précède : un compteur de génération et de population dans la barre d'état ; Reset vers l'état initial mémorisé ; avancer d'une seule génération (touche espace) ; détection automatique de stabilisation ou de période (section 3) ; sélecteur de règle et de topologie (sections 1 et 4).

### Gaps
- Les fonctionnalités de LifeViewer (le visualiseur intégré à LifeWiki : retour en arrière, thèmes d'historique) et de simulateurs en ligne comme copy.sh/life n'ont pas pu être vérifiées. Le résumé de recherche n'a rien remonté d'exploitable sur le retour en arrière ou l'âge dans LifeViewer.
