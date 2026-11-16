# Moteurs de calcul pour un très grand jeu de la vie fluide (JavaScript sur téléphone et Python/Tkinter)

> **Comment lire ces notes.** Chaque chiffre porte sa source. Les mentions **« Mesure locale »** désignent des micro-benchmarks lancés par le chercheur dans le bac à sable, le 16/11/2026. Machine : conteneur Linux, Intel Xeon @ 2,10 GHz (4 vCPU, 1 thread par cœur), 16 Go de RAM. Logiciels : Node v22.23.4 (moteur V8, le même que Chrome), Python 3.13.18, numpy 2.5.3 (scipy absent), Chrome for Testing 153 sans interface (rendu logiciel SwiftShader, **aucun vrai GPU**). Les scripts étaient dans `/tmp/claude-0/-home-user-jeu-de-la-vie-nsi/06f0f526-9e53-5054-8924-96e144a06f6d/scratchpad/bench/` (`life_js.js`, `life_js2.js`, `unpack.js`, `unpack2.js`, `pm.js`, `life_py.py`, `hashlife_py.py`) et `.../scratchpad/web/` (test d'iframe). Ce dossier temporaire peut être effacé. **Aucune mesure n'a été faite sur un vrai téléphone** : toutes les valeurs « téléphone » sont des extrapolations, signalées comme telles.
>
> **Accès réseau limité pendant la recherche.** Seuls github.com et raw.githubusercontent.com (plus pypi.org) étaient joignables. La documentation MDN a été lue depuis son dépôt source `mdn/content` sur GitHub, Golly depuis un miroir GitHub non officiel de SourceForge (AlephAlpha/golly), et WebKit depuis son dépôt GitHub. LifeWiki, conwaylife.com, web3dsurvey.com, nullprogram.com, Dr. Dobb's et les pages de John Williamson (johnhw.github.io) n'étaient pas joignables. Leurs chiffres ne viennent que d'extraits du moteur de recherche et sont marqués **(extrait de recherche, non relu en entier)**.

## 1. Disposition des données en JavaScript : objets, Uint8Array (1 octet par cellule) ou Uint32Array compacté (32 cellules par mot)

### Takeaway
Le compactage en bits (32 cellules par mot `Uint32Array`, voisines comptées par des additionneurs bit à bit) est de loin le plus rapide. Il tourne à environ 0,3 ns par cellule et par génération, soit environ 1,3 à 1,9 ms par génération pour 2048×2048 en mesure locale. C'est environ 9 à 13 fois plus rapide que la meilleure version à 1 octet par cellule (sommes glissantes de colonnes, environ 4 ns par cellule) et 40 à 150 fois plus rapide qu'un tableau d'objets (20 à 50 ns par cellule, environ 240 octets par cellule). Pour un damier de 2000×2000 qui doit rester fluide sur téléphone, c'est la seule disposition en JavaScript pur qui laisse de la marge pour l'affichage.

### Cited Findings
**Mesures locales.** Node 22, un seul thread, grille torique (les bords sont reliés), « soupe » aléatoire à 30 % de cellules vivantes. Chaque moteur tourne 0,8 s après 5 générations de chauffe. Les 7 moteurs donnent la même population après 60 générations sur une grille de contrôle de 128×96 (1512 cellules dans tous les cas). Valeurs en ns par cellule et par génération (générations par seconde entre parenthèses) :

| Moteur | 256×256 | 1024×1024 | 2048×2048 | 4096×4096 | Mémoire par cellule |
|---|---|---|---|---|---|
| A. Tableau d'objets `{etat, suivant, voisines:[8 réf.]}` (comme `Cellule`) | 21,3 (717) | 52,2 (18,3) | non lancé | non lancé | **≈ 240 o** |
| B. `Uint8Array`, 8 lectures, indices de bord précalculés | 6,3 (2420) | 6,8 (140) | 9,8 (24) | 7,6 (7,8) | 2 o (2 tampons) |
| C. Comme B, avec une table de règle `lut[etat*9+n]` | 7,6 (2010) | 6,1 (155) | 6,2 (39) | 10,7 (5,6) | 2 o |
| D. `Uint8Array` et sommes glissantes de colonnes (somme sur 3×3 incluant la cellule, naissance si 3, survie si 4) | 4,4 (3457) | 4,3 (221) | 4,05 (59) | 4,4 (13,5) | 2 o |
| E. **Bits dans un `Uint32Array`**, additionneurs complets bit à bit | **0,49 (31 437)** | **0,33 (2872)** | **0,31 (772)** | **0,36 (166)** | **0,25 o** (2 tampons) |
| F. Tuiles actives de 16×16 (sur B) | 9,2 | 7,2 | 7,4 | 6,9 | 2 o |
| G. Ensemble creux (`Set` + `Map` de compteurs) | 81 | 397 | non lancé | non lancé | ≈ 20 à 29 o par cellule de la grille |

— *Mesure locale* (`life_js.js`).
- Construire le tableau d'objets (moteur A) en 1024×1024 prend environ 0,4 à 0,55 s. Il occupe environ 240 octets par cellule mesurés par `heapUsed`, soit environ 250 Mo pour 1 million de cellules et environ 1 Go extrapolé pour 2000×2000. — *Mesure locale* (`life_js.js`).
- Les résultats varient d'une passe à l'autre. Par exemple, le moteur B en 2048² a donné 24 gén/s sur la soupe et 44 gén/s sur le motif creux. Il faut retenir des ordres de grandeur, pas des chiffres au pourcentage près. — *Mesure locale* (`life_js.js`).
- La table de règle (C) n'apporte presque rien par rapport à l'expression `(n===3)|(n===2&c)` (B). V8 compile déjà ce test sans branchement coûteux. Les sommes glissantes (D) gagnent environ 1,5 à 2 fois parce qu'elles font 3 additions par cellule au lieu de 8 lectures. — *Mesure locale* (`life_js.js`).
- Le noyau du moteur E (environ 25 opérations logiques par mot, donc pour 32 cellules) tel qu'il a été mesuré. Le bit i du mot correspond à la colonne 32·mot + i :
  ```js
  // A, B, C : mots de la ligne du dessus, de la ligne courante, de celle du dessous
  const nw=(A<<1)|(Aleft>>>31), ne=(A>>>1)|(Aright<<31);   // de même w/e avec B, sw/se avec C
  const x0=nw^A, s0=x0^ne, c0=(nw&A)|(ne&x0);              // ligne du haut = 2*c0 + s0
  const x2=sw^C, s2=x2^se, c2=(sw&C)|(se&x2);              // ligne du bas
  const s1=w^e,  c1=w&e;                                   // gauche + droite
  const y1=s0^s1, t=y1^s2, k1=(s0&s1)|(s2&y1);             // bit de poids 1 = t
  const p1=c0^c1, a1=c0&c1, p2=c2^k1, a2=c2&k1;
  const un=(p1^p2)&~(a1|a2);                               // exactement un bit de poids 2
  next = un & (t|B);                                       // total 3, ou total 2 et vivante
  ```
  — *Mesure locale* (`life_js.js`, fonction `makeBits`).
- Le moteur E impose ici une largeur multiple de 32. Pour 2000 colonnes, on arrondit à 2016 (63 mots) et on gère la colonne de repli du tore, ou bien on utilise des bords morts. — *Mesure locale* (contrainte du code testé).
- Un projet TypeScript publié (Jumbub/game-of-life-js) calcule 2000 générations d'un plateau torique de 2560×1440 (3,69 millions de cellules) en 2,55 s, soit **0,34 ns par cellule** en JS contre 0,15 ns en C++, sur un Intel i5-7600K à 4,4 GHz. Pour y arriver, il combine des `Uint8Array`, des « drapeaux de saut » par bloc, 4 workers, `SharedArrayBuffer` et `Atomics`. Son journal d'optimisation montre : première version 75 s, `Uint8Array` pour les sauts 53 s, `Uint8Array` pour les cellules 37 s, calcul dans un worker 28 s, worker dédié 19 s, plusieurs workers environ 12 s (4, 8 et 16 threads : 12,70 / 11,74 / 11,45 s), etc. Dernière remarque : `Atomics` (3,6 s) n'est que légèrement plus rapide que `postMessage` (3,8 s). — [Jumbub/game-of-life-js](https://github.com/Jumbub/game-of-life-js)
- Golly (QuickLife) stocke l'univers par « slices » de 4×8 cellules dans un mot de 32 bits. Une table de correspondance prend un carré 4×4 de la génération courante et donne les 2×2 cellules intérieures. Les « bricks » de 64 octets contiennent 8 slices pour la génération paire et 8 pour l'impaire (32×8 cellules), selon un schéma décalé (« stagger-step ») qui limite le nombre de voisines à examiner. — [Golly, gollybase/qlifealgo.h (miroir GitHub)](https://github.com/AlephAlpha/golly/blob/master/gollybase/qlifealgo.h)
- Pour une grille de 80×50, il faut 4000 octets en `Uint8Array` contre 500 en bits. L'auteur juge que le compactage n'en vaut pas la peine à moins d'avoir des grilles énormes. — [DEV Community, Uint8Array and canvas](https://dev.to/sendotltd/writing-conways-game-of-life-with-uint8array-and-canvas-including-a-gosper-glider-gun-1ppf) **(extrait de recherche, non relu en entier)**
- **Coût de l'affichage depuis les bits** (2048×2048 converti en pixels RGBA 1:1 dans un `Uint32Array`) : boucle naïve avec `if` 31,7 ms (mauvaises prédictions de branchement sur des données aléatoires), version sans branchement 7,2 ms, table 256×8 (un octet donne 8 pixels) 4,4 ms, contre 13,7 ms depuis un `Uint8Array`. En réduisant 2×2 cellules vers 1 pixel (1024×1024 pixels) : 5,3 ms. Pour 4096² en 1:1 avec la boucle naïve : 106 ms. — *Mesure locale* (`unpack.js`, `unpack2.js`)

### Inferences
- Avec le compactage en bits, **le calcul cesse d'être le goulot d'étranglement**. En 2048², une génération coûte environ 1,3 à 1,9 ms (mesure locale), alors que la conversion des cellules en pixels coûte de 4 à 30 ms selon le code. L'effort doit donc porter sur un affichage à la bonne échelle, avec une table de conversion et seulement la partie visible.
- Le tableau d'objets est à exclure côté web au-delà d'environ 500×500. Son coût en mémoire (environ 1 Go pour 2000×2000) le rend probablement inutilisable sur téléphone, même avant de parler de vitesse.
- Sans compactage, la meilleure option à 1 octet par cellule (sommes glissantes) donne environ 60 gén/s en 2048² sur la machine de test, et donc probablement 6 à 20 gén/s sur un téléphone moyen (voir section 8). C'est acceptable pour 1000×1000, limite pour 2000×2000.
- Ordre recommandé pour un développeur : 1) écrire une version de référence simple en `Uint8Array`, 2) écrire le moteur en bits, 3) comparer les deux sur quelques centaines de générations (c'est ce que fait la vérification croisée du script).

### Gaps
- Aucune mesure sur un vrai téléphone. Les chiffres viennent d'un Xeon de serveur à 2,1 GHz sous Node, pas de Safari iOS ni de Chrome Android.
- La variante « table de correspondance 4×4 vers 2×2 » de Golly ou la variante 16 bits n'ont pas été mesurées en JS. Le gain par rapport aux additionneurs bit à bit reste inconnu.
- Le tutoriel LifeWiki « bitwise SWAR Life » n'a pas pu être lu (hôte bloqué). Je n'ai pas de décompte d'opérations publié à citer.
- Je n'ai pas trouvé de comparaison publiée entre bits et octets en JavaScript : les moteurs de recherche ne renvoient que des mesures isolées.

## 2. Éviter le travail inutile : tuiles actives, ensembles creux de cellules vivantes, HashLife

### Takeaway
Ignorer les tuiles qui n'ont pas changé ne paie que sur des motifs **creux et calmes** : gain d'environ 5 à 9 fois à partir de 1024², mais seulement 1,6 fois en 256², avec quelques canons de Gosper sur un grand plateau vide. Sur une soupe aléatoire qui se « repose » sur un tore, presque rien n'est ignoré : 98 % des tuiles de 16×16 restent actives après 3000 générations, car les clignotants (période 2) sont partout. Un ensemble creux de cellules vivantes n'est compétitif que sous environ 1 % de densité. HashLife est imbattable sur les motifs réguliers (2^100 générations d'un canon en 0,1 s, même en Python), mais environ 100 fois plus lent qu'un moteur en bits sur une soupe chaotique (comparaison approximative : plan infini contre damier borné). Pour un damier fini de 2000×2000 rempli au hasard, le moteur en bits sans aucun saut est le meilleur choix par défaut.

### Cited Findings
- **Motif creux** (1 canon de Gosper pour 40 000 cellules, plateau vide), ns par cellule et par génération (générations par seconde) :

  | Moteur | 1024² | 2048² | 4096² |
  |---|---|---|---|
  | Octets, toutes cellules | 8,2 (116) | 5,4 (44) | 7,8 (7,7) |
  | Tuiles actives 16×16 | 1,58 (604), 992/4096 tuiles actives | 1,17 (204), 2842/16384 | 0,89 (67), 6937/65536 |
  | Ensemble creux | 1,32 (722) | 1,01 (236) | 1,08 (55) |
  | Bits, toutes cellules | 0,34 (2813) | 0,33 (712) | 0,38 (156) |

  — *Mesure locale* (`life_js.js`, motif `canons`)
- **Soupe reposée** (30 % au départ, puis 3000 générations sur un tore, densité finale d'environ 3,1 à 3,3 %) :

  | Plateau | Tuiles 16×16 | Ensemble creux | Bits complets |
  |---|---|---|---|
  | 1024² | 8,1 ms/gén, **4019/4096 tuiles toujours actives** | 35,5 ms/gén | 0,26 ms/gén |
  | 2048² | 33,4 ms/gén, 16 141/16 384 actives | 332 ms/gén | 1,87 ms/gén |

  — *Mesure locale* (`life_js2.js`)
- Sur une soupe dense (30 %), l'ensemble creux est catastrophique : 81 ns par cellule en 256² et 397 ns par cellule en 1024², soit 2,4 gén/s. — *Mesure locale* (`life_js.js`)
- Golly QuickLife suit les changements à plusieurs niveaux. Des drapeaux « c » par slice indiquent qu'une slice ou ses bords ont changé et que la brick voisine doit être recalculée. Les « tiles » regroupent 4 bricks (32×32 cellules) et contiennent deux compteurs de population de 12 bits et des drapeaux. Les « supertiles » forment un arbre (256×32, puis 256×256…). Une zone vide pointe vers une brick vide unique partagée. — [Golly, qlifealgo.h](https://github.com/AlephAlpha/golly/blob/master/gollybase/qlifealgo.h)
- HashLife utilise l'algorithme de Bill Gosper pour atteindre des vitesses remarquables sur les motifs très réguliers dans le temps ou l'espace. Golly précise : « HashLife performs very poorly on highly chaotic patterns », et conseille alors de passer à QuickLife. — [Golly Help: HashLife (miroir GitHub)](https://github.com/AlephAlpha/golly/blob/master/Help/Algorithms/HashLife.html)
- Dans l'implémentation hlife de Golly (Rokicki), un nœud contient 5 pointeurs (lien de hachage, `nw`, `ne`, `sw`, `se`) plus un pointeur `res` qui mémorise le résultat. Les feuilles sont des carrés de 8×8 représentés par quatre `unsigned short` de 4×4, et leur résultat (le carré 4×4 central, 2 générations plus tard) est calculé dès leur création par une table de règle. — [Golly, hlifealgo.h](https://github.com/AlephAlpha/golly/blob/master/gollybase/hlifealgo.h) ; [hlifealgo.cpp](https://github.com/AlephAlpha/golly/blob/master/gollybase/hlifealgo.cpp)
- Selon l'article de Rokicki (« An Algorithm for Compressing Space and Time », Dr. Dobb's Journal, avril 2006), HashLife combine des arbres quaternaires (quadtrees) et la mémoïsation. Il fait tourner certains univers pendant des milliers de milliards de générations alors qu'ils grossissent jusqu'à des milliards de cellules. La première version de l'article n'était pas meilleure : plus de mémoire et plus lente. HashLife est très rapide sur les motifs périodiques mais épuise vite la mémoire sur les motifs chaotiques. — [Dr. Dobb's](https://drdobbs.com/cpp/an-algorithm-for-compressing-space-and-t/184406478) **(extrait de recherche, non relu en entier)**
- **HashLife minimal en Python** (≈ 70 lignes, écrit par le chercheur d'après le schéma de Gosper, `lru_cache` pour la mémoïsation, plan infini) :

  | Motif | Générations | Temps | Nœuds créés |
  |---|---|---|---|
  | Canon de Gosper | 2^10 | 6,7 ms | 2731 |
  | Canon de Gosper | 2^20 | 16,7 ms | 5431 |
  | Canon de Gosper | 2^30 | 23,5 ms | 8121 |
  | Canon de Gosper | 2^100 | 99,7 ms | 26 951 |
  | Soupe 64×64 | 1000 | 0,25 s | 66 586 |
  | Soupe 128×128 | 1000 | 2,10 s | 283 913 |
  | Soupe 256×256 | 1000 | 7,90 s | 808 121 |

  Les populations du canon sont vérifiées : 36 à t=0, 41 à t=30, 56 à t=120, 174 804 à t=2^20. Pour comparaison, l'entier géant Python (section 7) fait 1000 générations de 440×280 en environ 66 ms. — *Mesure locale* (`hashlife_py.py`, `life_py.py`)
- Une implémentation Python de référence de HashLife, avec une explication détaillée, existe ; un équivalent en C ISO est fourni. — [johnhw/hashlife](https://github.com/johnhw/hashlife)

### Inferences
- **Pourquoi les tuiles ne servent à rien sur une soupe reposée.** Une tuile n'est sautée que si elle *et ses 8 voisines* n'ont pas changé. Un clignotant change à chaque génération et garde actives 9 tuiles. Avec environ un oscillateur pour quelques centaines de cellules, presque toutes les tuiles de 16×16 restent actives. Pour en tirer profit, il faudrait détecter la période 2 (comparer l'état t à l'état t−2 et recopier t−1) ou utiliser de très petites tuiles, ce qui alourdit le code. C'est une piste d'optimisation, pas un premier choix.
- **Quand chaque technique paie, version élève :**
  - le moteur en bits, toutes cellules : coût proportionnel à la *surface* (largeur × hauteur / 32), toujours le même, idéal pour une grille finie remplie ;
  - les tuiles actives : coût proportionnel à la surface *qui bouge* ; utile pour quelques motifs dans un grand vide ;
  - l'ensemble creux : coût proportionnel au *nombre de cellules vivantes* × 9 ; utile sous environ 1 % de densité, ou pour une grille infinie ;
  - HashLife : coût lié au nombre de *motifs distincts* rencontrés ; peut avancer de 2^k générations d'un coup sur un motif régulier, mais devient mauvais quand tout est différent partout (soupe).
- **HashLife expliqué à un élève.** On découpe la grille en 4 carrés, puis chaque carré en 4, et ainsi de suite. Deux carrés identiques ne sont stockés qu'une fois (dictionnaire). Pour chaque carré de côté 2^k, on retient dans un dictionnaire « à quoi ressemblera son centre dans 2^(k−2) générations ». Comme les mêmes petits carrés reviennent sans cesse (blocs, planeurs…), on réutilise les résultats au lieu de recalculer.
- HashLife suppose un plan infini et des puissances de 2. Pour un damier torique de 2000×2000 affiché à chaque génération, il est peu adapté : on veut voir chaque génération, pas sauter des milliards de générations. Je ne l'utiliserais que dans un mode spécial « avance rapide » sur des motifs.

### Gaps
- Je n'ai pas mesuré de tuiles actives *sur la version en bits* (à la manière de QuickLife), ni de détection de la période 2 : l'effet sur une soupe reposée reste à mesurer.
- Je n'ai pas pu lire l'article de Rokicki en entier (hôte bloqué). Ses chiffres exacts de mémoire et de vitesse ne sont donc pas cités.
- Golly gère les grilles bornées et toriques avec HashLife, mais je n'ai pas trouvé de source lisible qui explique comment.

## 3. GPU : WebGL, rendu alterné entre deux textures (ping-pong), limites de taille de texture, textures flottantes ou d'octets, relecture de la population

### Takeaway
Un damier de 2000×2000, et même de 4000×4000, tient dans une texture de 4096 de côté, taille que MDN considère comme supportée par « effectivement tous les systèmes ». Le rendu alterné entre deux textures en RGBA8 (`UNSIGNED_BYTE`), le seul format de rendu garanti, est simple et bien documenté. Le calcul GPU est très rapide (WebGOL annonce 120 millions de mises à jour de cellules par seconde sur un iGPU Intel HD 4000 de portable), et l'affichage est gratuit puisque l'état est déjà dans une texture. Le point faible est de **relire** l'état ou la population vers le CPU (`readPixels` est synchrone et bloquant). Pour 2000×2000, cela vaut la peine si l'on accepte de faire les comptages (population, hachage) sur le GPU ou rarement. Sinon, le moteur CPU en bits suffit probablement.

### Cited Findings
- MDN, WebGL best practices : « In practice, effectively all systems support at least the following: … `MAX_RENDERBUFFER_SIZE: 4096`, `MAX_TEXTURE_SIZE: 4096`, `MAX_VIEWPORT_DIMS: [4096,4096]` ». — [MDN, WebGL best practices](https://developer.mozilla.org/en-US/docs/Web/API/WebGL_API/WebGL_best_practices)
- Web3D Survey (WebGL 2) : ≥ 4096 pour 100 % des rapports, ≥ 8192 pour 98 %, ≥ 16384 pour 86 %. Sur Android, ≥ 8192 pour 75 % et ≥ 16384 pour 34 %. La page WebGL 1 donne 8192 pour 87,59 %. Les deux pages ne concordent pas. — [web3dsurvey, MAX_TEXTURE_SIZE (WebGL 2)](https://web3dsurvey.com/webgl2/parameters/MAX_TEXTURE_SIZE) **(extrait de recherche, non relu : hôte bloqué)**
- Un chiffre plus ancien (2020) : 99 % des appareils supportent 4096, mais seulement 50 % plus de 4096. La taille maximale est une dimension et ne garantit pas que le GPU ait assez de mémoire pour une texture de cette taille au carré. — [WebGL2 Fundamentals, cross-platform issues](https://webgl2fundamentals.org/webgl/lessons/webgl-cross-platform-issues.html)
- Seules quelques combinaisons d'attachements de framebuffer sont garanties, la première étant « a single format = `RGBA`, type = `UNSIGNED_BYTE` texture as `COLOR_ATTACHMENT0` ». Beaucoup d'appareils mobiles ne supportent pas le filtrage des textures flottantes (`OES_texture_float_linear`). — [WebGL2 Fundamentals, cross-platform issues](https://webgl2fundamentals.org/webgl/lessons/webgl-cross-platform-issues.html)
- « Don't assume you can render into float textures ». En WebGL 2, il faut vérifier `EXT_color_buffer_float`. Avec une texture flottante, iOS exige `highp sampler2D` sous peine d'échantillons en `lowp`. En WebGL 1, `highp float` est optionnel dans les fragment shaders, et `mediump` corrompt souvent le rendu sur mobile. — [MDN, WebGL best practices](https://developer.mozilla.org/en-US/docs/Web/API/WebGL_API/WebGL_best_practices)
- `readPixels()` vers le CPU provoque « finish + round-trip » (le GPU termine tout, puis un aller-retour). MDN recommande en WebGL 2 une relecture asynchrone : `readPixels` vers un tampon `PIXEL_PACK`, puis une barrière (fence) et `getBufferSubData`. — [MDN, WebGL best practices](https://developer.mozilla.org/en-US/docs/Web/API/WebGL_API/WebGL_best_practices)
- Principe du ping-pong : le shader s'exécute une fois par pixel. L'état ne peut pas être modifié en place, il alterne donc entre deux textures en mémoire GPU. Mettre plusieurs cellules par pixel réduirait le parallélisme. — [nullprogram, A GPU Approach to Conway's Game of Life](https://nullprogram.com/blog/2014/06/10) **(extrait de recherche, non relu en entier)**
- Le code de référence de skeeto crée deux textures `front` et `back` en `gl.RGBA`, avec `gl.REPEAT` (ce qui donne le tore gratuitement) et `gl.NEAREST`. Il envoie l'état sous forme d'un `Uint8Array` RGBA de 4 octets par cellule et échange les textures à chaque pas (`swap`). — [skeeto/webgl-game-of-life, js/gol.js](https://github.com/skeeto/webgl-game-of-life/blob/master/js/gol.js)
- WebGOL : « Even with a low-power GPU in a laptop (eg: Intel HD Graphics 4000), WebGOL can run a 1080p simulation at 60 frames-per-second (120 million cell updates every second) ». — [michaelhogg/webgol](https://github.com/michaelhogg/webgol)
- Une variante compactée (piellardj) fait le compactage et le décompactage dans les fragment shaders avec des flottants, car WebGL 1 n'autorise ni les textures entières ni les opérateurs bit à bit. — [piellardj/game-of-life-webgl (fiche ecosyste.ms)](https://awesome.ecosyste.ms/projects/github.com%2Fpiellardj%2Fgame-of-life-webgl) **(extrait de recherche)**
- *Mesure locale* (Chrome 153 sans interface, SwiftShader, donc sans vrai GPU) : WebGL 2 est disponible **dans une iframe `sandbox="allow-scripts"`**, avec `MAX_TEXTURE_SIZE` = 8192 et `EXT_color_buffer_float` présent. Ces valeurs viennent du rendu logiciel et ne représentent pas un téléphone. — *Mesure locale* (`scratchpad/web/inner.js`)

### Inferences
- **Mémoire GPU** : une texture RGBA8 de 2000² occupe 16 Mo, donc 32 Mo pour les deux du ping-pong. En 4000², 64 Mo chacune, soit 128 Mo. En WebGL 2, une texture `R8` (1 octet par texel) divise par 4 : 4 Mo par texture en 2000². C'est un calcul, il ne tient pas compte de l'alignement interne des pilotes.
- **Population** : relire 2000² en RGBA8, c'est 16 Mo par génération en lecture synchrone. Mieux vaut réduire sur le GPU par passes successives (2×2 vers 1 pixel, environ 11 passes pour 2000², jusqu'à 1 pixel) puis lire 1 pixel, ou relire de façon asynchrone et seulement toutes les N générations.
- **La détection de cycles et l'annulation deviennent difficiles avec le GPU**, car l'état n'est plus côté JS. Il faudrait hacher sur le GPU ou relire l'état périodiquement. C'est le vrai coût de complexité.
- **Est-ce que ça vaut la peine pour 2000×2000 ?** Le moteur CPU en bits calcule une génération de 4 millions de cellules en environ 1,3 à 1,9 ms (mesure locale), soit probablement 4 à 15 ms sur un téléphone moyen (extrapolation, section 8). Le GPU ne s'impose donc qu'au-delà, en 4000² et plus, ou pour plusieurs générations par image. Il demande en plus une solution de repli si WebGL est absent ou si le contexte est perdu, ce qui arrive sur mobile.
- Au-delà de 4096 de côté, il faut découper en plusieurs textures, ou vérifier `MAX_TEXTURE_SIZE` à l'exécution : 8192 est probable mais pas garanti, surtout sur Android.

### Gaps
- Aucune mesure de vitesse WebGL sur téléphone n'a été trouvée ou faite. Le seul chiffre de débit (120 M cellules/s) date d'un iGPU de portable d'environ 2012.
- La répartition de `MAX_TEXTURE_SIZE` par plateforme (iOS ou Android) n'a été vue que dans un extrait de recherche. Les pourcentages exacts sont à reconfirmer sur web3dsurvey.com.
- Je ne sais pas à quelle fréquence le contexte WebGL est perdu sur mobile (`webglcontextlost`) : aucune source trouvée.

## 4. Web Workers : calcul hors du thread principal, ArrayBuffer transférables ou SharedArrayBuffer, coût d'un postMessage par image

### Takeaway
`SharedArrayBuffer` exige que la page soit « isolée entre origines » (en-têtes COOP et COEP envoyés par le serveur). Une page statique dans une iframe sandboxée qu'on ne contrôle pas n'y a pas accès : en mesure locale, `SharedArrayBuffer` n'est même pas défini. En revanche, **un Worker créé depuis un Blob fonctionne dans une iframe `sandbox="allow-scripts"`** (testé dans Chrome). Transférer un `ArrayBuffer` coûte environ 0,06 à 1 ms l'aller-retour quelle que soit sa taille (0,06 à 0,33 ms dans l'iframe sandboxée), alors que le copier coûte de quelques ms à plus de 100 ms pour 16 Mo. Pour 2000×2000, un worker qui renvoie à chaque image un tampon de bits (500 Ko) ou de pixels par transfert est viable. Avec un moteur en bits très rapide, le worker sert surtout à garder l'interface fluide, pas à gagner en débit.

### Cited Findings
- MDN : « To use shared memory your document must be in a secure context and cross-origin isolated ». Sinon, `SharedArrayBuffer` n'est pas défini. — [MDN, SharedArrayBuffer](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/SharedArrayBuffer)
- Pour être isolé entre origines, un document doit être servi avec `Cross-Origin-Opener-Policy: same-origin` **et** `Cross-Origin-Embedder-Policy: require-corp` ou `credentialless`, et la directive `cross-origin-isolated` de `Permissions-Policy` ne doit pas le bloquer. Sinon, `crossOriginIsolated` vaut `false`. — [MDN, Window.crossOriginIsolated](https://developer.mozilla.org/en-US/docs/Web/API/Window/crossOriginIsolated)
- Transférer un `ArrayBuffer` le déplace « in a fast and efficient zero-copy operation », et le tampon d'origine devient inutilisable (`byteLength` 0). — [MDN, Transferable objects](https://developer.mozilla.org/en-US/docs/Web/API/Web_Workers_API/Transferable_objects)
- *Mesure locale*, Chrome 153 sans interface, page servie en `http://localhost`, trois iframes :

  | Iframe | Origine | `crossOriginIsolated` | `SharedArrayBuffer` | `localStorage` | Worker Blob |
  |---|---|---|---|---|---|
  | `sandbox="allow-scripts"` | `"null"` | false | **non défini** | refusé (`SecurityError`) | **construit et fonctionnel** |
  | `sandbox="allow-scripts allow-same-origin"` | `http://localhost:8765` | false | non défini | accessible | fonctionnel |
  | sans sandbox | `http://localhost:8765` | false | non défini | accessible | fonctionnel |

  — *Mesure locale* (`scratchpad/web/inner.js`, `cdp.js`)
- *Mesure locale*, aller-retour `postMessage` entre la page et le worker dans l'iframe sandboxée :

  | Tampon | Transfert | Copie (clonage structuré) |
  |---|---|---|
  | 512 Ko (2048² en bits) | 0,08 ms | 22,8 ms |
  | 4 Mo (2048² en octets) | 0,33 ms | 42 ms |
  | 16 Mo (4096² en octets) | 0,12 ms | 141 ms |

  Les copies sous Chrome sans interface semblent anormalement lentes. Sous Node `worker_threads`, la copie aller-retour mesure 1,3 ms (512 Ko), 4,1 ms (4 Mo) et 17,9 ms (16 Mo), et le transfert environ 0,06 ms. — *Mesure locale* (`inner.js`, `pm.js`)
- Jumbub a mesuré `Atomics` et `SharedArrayBuffer` à 3,6 s contre 3,8 s avec `postMessage` pour le même calcul, soit un gain faible. Les gains importants venaient d'un worker de calcul dédié (28 s, puis 19 s) et de plusieurs workers (environ 12 s). — [Jumbub/game-of-life-js](https://github.com/Jumbub/game-of-life-js)
- `OffscreenCanvas` est disponible dans l'iframe sandboxée testée. — *Mesure locale* (`inner.js`)

### Inferences
- **Architecture viable sans `SharedArrayBuffer`** : le worker garde l'état en bits et calcule N générations. Il remplit un tampon de pixels à l'échelle de l'écran (ou renvoie les bits) et le *transfère* au thread principal, qui le *transfère* en retour une fois dessiné. On alterne deux tampons. Le coût de messagerie (moins de 1 ms) devient négligeable devant le budget d'une image de 16,7 ms.
- Si l'iframe cible n'a pas `allow-same-origin`, `localStorage` est refusé. La documentation de l'outil Artifact affirme pourtant que `localStorage` fonctionne, ce qui laisse penser que les artifacts ont une origine propre. Dans les deux cas, `SharedArrayBuffer` reste indisponible faute d'en-têtes COOP/COEP.
- Avec un seul worker, on ne gagne pas de débit, seulement de la fluidité pour l'interface (gestes, boutons). Avec plusieurs workers et sans mémoire partagée, il faudrait découper en bandes et échanger les lignes de bord à chaque génération : complexe, et peu utile vu la vitesse du moteur en bits.
- Il faut toujours prévoir de retomber sur un calcul dans le thread principal si `new Worker(blobURL)` lève une exception.

### Gaps
- Le comportement de `new Worker(URL.createObjectURL(blob))` dans une iframe sandboxée **sous Safari iOS** n'a pas été testé (aucun Safari disponible) et je n'ai pas trouvé de source. C'est un risque à vérifier sur un appareil réel.
- Les en-têtes et attributs `sandbox` exacts de l'iframe d'Artifact claude.ai ne sont pas connus.
- La lenteur des copies sous Chrome sans interface (20 à 140 ms) n'est pas expliquée. C'est peut-être un artefact du mode sans interface ou du conteneur.

## 5. Limites mémoire des navigateurs mobiles (typed arrays, canvas) et coût d'un historique d'annulation de grilles complètes

### Takeaway
Les tableaux typés d'un damier de 2000×2000 sont petits : 4 Mo en octets, 500 Ko en bits. Ce qui fait exploser la mémoire, ce sont (1) un historique de grilles complètes non compactées (500 grilles d'octets en 2000², c'est 2 Go) et (2) les canvas sur iOS, qui ont une surface maximale (aujourd'hui 8192×8192 pixels dans le code de WebKit pour iOS, 4096×4096 sur d'anciennes versions) et une limite de mémoire totale pour les canvas, rapportée entre 224 et 384 Mo selon la version et l'appareil. Il faut stocker l'historique en bits et/ou par points de reprise que l'on recalcule.

### Cited Findings
- Le code actuel de WebKit fixe la surface maximale d'un canvas à `8192 * 8192` pixels physiques sous `PLATFORM(IOS_FAMILY)`, et `16384 * 16384` ailleurs. Au-delà, il émet « Canvas area exceeds the maximum limit (width * height > …) ». — [WebKit, Source/WebCore/html/CanvasBase.cpp](https://github.com/WebKit/WebKit/blob/main/Source/WebCore/html/CanvasBase.cpp)
- D'anciennes versions d'iOS rejetaient les canvas au-delà de 16 777 216 pixels (4096²) : « Canvas area exceeds the maximum limit (width * height > 16777216) on iOS ». — [Lightrun, react-pdf issue](https://lightrun.com/answers/wojtekmaj-react-pdf-canvas-area-exceeds-the-maximum-limit-width--height--16777216-on-ios) **(extrait de recherche)**
- « Total canvas memory use exceeds the maximum limit » : 384 Mo sur iOS 15 selon PQINA, moins sur les versions antérieures, probablement aussi selon l'appareil. Autres valeurs rapportées : 224 Mo (iOS 12+), 256 Mo (Safari 12), 576 Mo (iPad). Le canvas reste alors blanc. Contournement : réduire les canvas ou les libérer en mettant leurs dimensions à 0. — [PQINA](https://www.pqina.nl/blog/total-canvas-memory-use-exceeds-the-maximum-limit/) ; [Apple Developer Forums (224 MB)](https://developer.apple.com/forums/thread/112218) **(extraits de recherche, non relus en entier)**
- Chaque couple navigateur/plateforme impose ses propres limites de taille de canvas. Les navigateurs ne permettent pas de les connaître et ne signalent rien quand un canvas trop grand devient inutilisable, d'où la bibliothèque `canvas-size` qui les teste à l'exécution. — [jhildenbiddle/canvas-size](https://github.com/jhildenbiddle/canvas-size)
- Tailles mesurées pour l'historique : une copie `u8.slice()` coûte 0,71 ms en 2048² (4 Mo) et 5,9 ms en 4096² (16 Mo). Une copie `bits.slice()` coûte 0,05 ms en 2048² (512 Ko) et 0,34 ms en 4096² (2 Mo). — *Mesure locale* (`life_js2.js`)
- Projet Python actuel : 500 photos d'historique (`TAILLE_HISTORIQUE`) font 62 Mo en 440×280 (1 octet par cellule) et 2 Go en 2000×2000, ou 250 Mo compactées en bits. — *Mesure locale / calcul* (`jdlv.py` et script de mesure du hachage Python)

### Inferences
- **Budget mémoire d'un damier de 2000×2000 en bits** : 2 tampons de 500 Ko + un tampon de pixels à l'échelle de l'écran (par exemple 1080×1080×4 = 4,7 Mo) + un historique. Tout reste bien sous 50 Mo si l'historique est en bits et limité.
- **Historique par points de reprise** : comme le jeu de la vie est déterministe, on peut garder une grille en bits toutes les K générations (par exemple K=32) et recalculer jusqu'à K−1 générations pour revenir en arrière. En 2000² avec le moteur en bits, recalculer 31 générations coûte environ 31 × 1,5 ms ≈ 50 ms sur la machine de test, probablement 0,15 à 0,5 s sur téléphone (extrapolation). Ainsi, 500 générations d'annulation ne demandent que 16 points de reprise × 500 Ko = 8 Mo.
- Il faut éviter un canvas de 2000×2000 « 1 cellule = 1 pixel physique » multiplié par `devicePixelRatio` (3 sur beaucoup de téléphones, soit 6000×6000 = 36 M pixels, sous la limite de 67 M d'iOS mais environ 144 Mo de mémoire de canvas). Mieux vaut un canvas à la taille de l'écran et dessiner la partie visible.

### Gaps
- Je n'ai trouvé aucune source fiable sur la mémoire maximale par onglet (iOS Safari, Chrome Android) ni sur la taille maximale d'un `ArrayBuffer` sur mobile. Les tailles en jeu ici (moins de 20 Mo) sont très probablement sans risque, mais ce n'est pas sourcé.
- La formule de WebKit pour la mémoire totale des canvas (`maxPixelMemory = std::max(ramSize() / 4, 2151 * MB)`, vue dans un extrait de rapport de bogue) n'a pas été vérifiée dans le code actuel. La recherche de `maxActivePixelMemory` dans `HTMLCanvasElement.cpp` et `CanvasBase.cpp` n'a rien donné.

## 6. Détection de cycles sur très grandes grilles : hachage de la grille (64 bits ou deux voies de 32 bits), probabilité de collision, coût par génération

### Takeaway
Hacher la grille compactée en bits coûte environ 0,17 à 0,25 ms par génération en 2048² en JS (FNV 32 bits ou deux voies de 32 bits avec `Math.imul`), 8 à 13 fois moins que sur la grille en octets. Une empreinte de 32 bits ne suffit pas sur une longue partie : avec 3000 états mémorisés, le risque de fausse alerte est d'environ 7×10⁻⁷ par génération, donc probable sur un million de générations. Deux voies de 32 bits (64 bits en tout) suffisent si l'on **vérifie la grille complète en cas de coïncidence**. Le projet Python actuel garde des signatures complètes : 370 Mo en 440×280 pour 3000 états, et 12 Go en 2000².

### Cited Findings
- Coût du hachage en JS par génération :

  | Plateau | FNV-1a 32 bits, grille en bits | 2×32 bits, grille en bits | FNV, grille en octets (vue `Uint32`) | 2×32, grille en octets |
  |---|---|---|---|---|
  | 1024² | 0,041 ms | 0,064 ms | 0,35 ms | 0,50 ms |
  | 2048² | 0,165 ms | 0,247 ms | 1,54 ms | 2,26 ms |
  | 4096² | 0,69 ms | 1,03 ms | 9,3 ms | 12,2 ms |

  Un FNV 64 bits en `BigInt` coûte 2,08 ms en 1024², environ 50 fois plus que la version 32 bits, à éviter. — *Mesure locale* (`life_js2.js`)
- Python, 2000×2000 : `hash(a.tobytes())` 1,53 ms (sérialisation comprise), `hash(np.packbits(a).tobytes())` 0,46 ms, BLAKE2b de 8 octets sur les bits 0,70 ms, `zlib.crc32` sur les bits 0,11 ms. En 440×280, `hash(bytes)` coûte 0,035 ms. — *Mesure locale*
- La fonction `hash()` de Python pour `str` et `bytes` utilise SipHash, une fonction pseudo-aléatoire à graine de 128 bits, avec une sortie de 64 bits sur les plateformes 64 bits. — [PEP 456](https://peps.python.org/pep-0456/)
- Le projet actuel utilise comme clé de `deja_vus` la signature `bytes(cellule.Etat for cellule in self.cellules())`, soit 1 octet par cellule, avec jusqu'à `TAILLE_MEMOIRE = 3000` états. Cela fait 123 200 octets par clé en 440×280, environ 370 Mo pour 3000 clés, et 12 Go en 2000². Calculer la signature plus l'historique (`_memoriser_etat_actuel`) coûte 2,0 ms par génération en 200×130 et 12,2 ms en 440×280. — *Lecture du code* (`/home/user/jeu-de-la-vie-nsi/jdlv.py`) *et mesure locale* (`life_py.py`)

### Inferences
- **Probabilité de collision (paradoxe des anniversaires, calcul).** Avec n empreintes mémorisées sur b bits, la probabilité qu'un nouvel état coïncide par hasard avec l'une d'elles vaut environ n / 2^b :
  - b = 32, n = 3000 : environ 7×10⁻⁷ par génération, donc environ 50 % de chances d'une fausse alerte sur un million de générations ;
  - b = 64 : environ 1,6×10⁻¹⁶ par génération, négligeable.

  La probabilité qu'*au moins une paire* parmi n états coïncide vaut environ n² / 2^(b+1) : environ 10⁻³ pour n = 3000 et b = 32.
- **Recette sûre** : une table `Map` de l'empreinte 64 bits (deux voies de 32 bits concaténées en clé, par exemple `h1 * 2**32 + h2` ou une chaîne) vers le numéro de génération. En cas de coïncidence, on compare la grille complète à la grille gardée en bits, ou on rejoue la simulation depuis le point de reprise. On n'a alors **aucune fausse alerte**, pour 8 à 16 octets par état au lieu de W×H.
- **Raccourcis bon marché** : comparer d'abord l'état t avec t−1 (configuration stable) et t−2 (période 2, le cas le plus fréquent des soupes reposées, à cause des clignotants) avec une simple comparaison de mots en bits, qui coûte environ le prix d'un hachage. Ne hacher que toutes les k générations réduit le coût, au prix d'une détection retardée.
- Les deux voies doivent avoir des multiplicateurs ou des mélanges différents pour être à peu près indépendantes. Ce n'est pas une garantie cryptographique, d'où la vérification complète.

### Gaps
- Je n'ai pas trouvé de source publiée sur les propriétés statistiques d'un FNV doublé ou des hachages à deux voies de 32 bits en JS. Le calcul de probabilité suppose un hachage idéal.
- La prise en compte du **décalage** (un planeur sur un tore revient au même état après un tour complet ; un vaisseau dans un plan infini ne revient jamais exactement) n'a pas été étudiée ici. Sur un tore, la période peut être très longue, comme le note le commentaire de `jdlv.py` (planeur seul sur 70×45 : 2520 tours).

## 7. Côté Python (Tkinter) : pourquoi une liste d'objets Cellule avec listes de voisines est lente, et quelles alternatives

### Takeaway
Le moteur actuel (objets `Cellule` reliés par des listes de voisines) coûte environ **320 à 340 ns par cellule pour le seul calcul**, et environ 450 à 610 ns avec l'historique et la signature. Il occupe environ **240 octets par cellule**. Cela donne 63 gén/s en 200×130 mais seulement environ 18 gén/s en 440×280. Sans quitter Python pur, une liste plate d'entiers avec des indices de voisines précalculés est 2,5 à 3 fois plus rapide. Un **entier Python géant utilisé comme damier de bits** (SWAR) atteint 15 000 gén/s en 440×280 et 380 gén/s en 2000×2000. numpy donne 10 000 gén/s en 440×280. Les classes `Cellule` et `Jdlv` peuvent rester l'interface, avec un moteur compact derrière.

### Cited Findings
- **Mesures locales** (Python 3.13, grille torique sauf pour l'entier géant, à bords morts, soupe à 30 %), en ms par génération (générations par seconde, ns par cellule) :

  | Moteur | 200×130 (26 000 cellules) | 440×280 (123 200 cellules) | 2000×2000 |
  |---|---|---|---|
  | `Jdlv.tour_suivant()` du projet (calcul + historique + signature + analyse) | 15,9 (63 ; 610) | 55,8 (17,9 ; 453) | non lancé |
  | … dont calcul `Cellule` seul (`calculer_etat_suivant` + `passer_a_l_etat_suivant`) | 8,4 (119 ; 323) | 42,3 (23,6 ; 343) | non lancé |
  | … dont `_memoriser_etat_actuel` | 2,0 | 12,2 | non lancé |
  | Liste plate d'entiers + tuples d'indices des voisines + table de règle | 3,0 (330 ; 117) | 16,7 (60 ; 136) | non lancé |
  | Ensemble de vivantes + `collections.Counter` | 3,4 (296), pop. ≈ 1373 | 126 (7,9), pop. ≈ 24 754 | non lancé |
  | numpy `np.roll` (8 décalages) | 0,11 (8700) | 0,23 (4300) | 9,8 (102) |
  | numpy, tranches sur un tableau bordé, sans allocation | 0,046 (21 965) | 0,094 (10 643) | 5,2 (193) |
  | **Entier Python géant** (1 bit par cellule, mêmes additionneurs que le moteur JS en bits) | 0,014 (71 873) | 0,066 (15 060) | 2,6 (379) |

  Vérifications : le projet et numpy donnent la même population (208) après 20 générations sur 40×30 torique ; l'entier géant et numpy à bords morts donnent tous deux 115. — *Mesure locale* (`life_py.py`)
- Mémoire de `Jdlv(W, H)` mesurée avec `tracemalloc` : **241 octets par cellule** (objet `Cellule`, son `__dict__` à 4 attributs, la liste de 8 références vers les voisines, les listes de la grille), en 200×130 comme en 440×280. — *Mesure locale* (`life_py.py`)
- David Buchanan (« SIMD in Pure Python », janvier 2024) utilise les entiers géants de Python comme des registres SIMD. Il annonce un jeu de la vie en Python pur (pysdl2 pour l'affichage) en 4K à 180 images/s, environ 3800 fois plus rapide qu'une version naïve. Une autre version de la même idée stocke 4 bits par cellule dans un seul entier pour compter les voisines sans débordement, et cite 1080p à 60 images/s, soit 124 416 000 cellules par seconde. — [Article (miroir gwern.net)](https://gwern.net/doc/www/www.da.vidbuchanan.co.uk/7b823654e531e7439a92c79369c375b2a87a8998.html) ; [notes.billmill.org](https://notes.billmill.org/link_blog/2024/01/SIMD_in_pure_python.html) **(extraits de recherche)**
- Le dépôt `pyswargol` confirme le principe : des threads « Life » calculent l'algorithme SWAR par bandes horizontales, et des threads « Blitter » décompactent les tampons SWAR en surfaces RGBA8888 via SDL2 (« 4 bits per cell, to match the buffer format of the optimised version »). — [DavidBuchanan314/pyswargol](https://github.com/DavidBuchanan314/pyswargol)
- La fonction `signature()` du projet parcourt toutes les cellules (`bytes(cellule.Etat for …)`) et elle est appelée deux fois par génération (`_memoriser_etat_actuel` puis `_analyser`). Au total, `tour_suivant()` coûte 1,3 à 1,9 fois le calcul seul. — *Lecture du code* (`jdlv.py`) *et mesure locale*

### Inferences
- **Pourquoi c'est lent (à expliquer à un élève)** : pour chaque cellule et chaque génération, Python fait environ 4 appels de méthode (`calculer_etat_suivant`, `nombre_voisines_vivantes`, `regle.etat_suivant`, `passer_a_l_etat_suivant`), une boucle `for` sur 8 voisines (8 accès à l'attribut `Etat` via un dictionnaire) et un test `in` sur un ensemble. Chaque étape traverse l'interpréteur et coûte quelques dizaines de ns, d'où environ 330 ns par cellule. numpy ou l'entier géant font la même opération sur *toute la grille* en une seule instruction écrite en C : le surcoût de l'interpréteur est payé une fois par génération, pas une fois par cellule.
- **Proposition compatible avec le sujet** : garder `Cellule` (attribut `Etat`) et `Jdlv` (attribut `grille`, `tour`, `start()`), mais faire calculer `tour_suivant()` avec un moteur compact (liste plate, numpy, ou entier géant si numpy n'est pas autorisé), puis resynchroniser seulement les `Etat` des cellules qui ont changé, ou rendre `Etat` calculé à la demande. À vérifier avec l'enseignant : le sujet impose peut-être que chaque `Cellule` calcule son propre état.
- Le passage à `__slots__` dans `Cellule` réduirait la mémoire et un peu le temps. Non mesuré ici, ce n'est donc qu'une hypothèse.
- **L'affichage Tkinter devient le goulot** dès que le calcul est rapide : 123 200 rectangles en 440×280 sur un `Canvas` coûtent très probablement plus cher que le calcul en numpy ou en entier géant. Une image unique (`PhotoImage`) mise à jour d'un bloc est la piste habituelle (non mesuré ici).
- Pour le tore avec l'entier géant, il faut ajouter le repli des bords (recopier la première et la dernière colonne et ligne, ou faire des rotations de bits). C'est un surcoût modeste, non mesuré.
- Signatures : remplacer la clé `bytes` complète par `hash(np.packbits(...).tobytes())` ou par l'entier géant lui-même (`hash(v)`), avec vérification en cas de coïncidence. On divise la mémoire de `deja_vus` par plus de 1000 (8 octets d'empreinte plus le coût de l'entrée du dictionnaire, contre 123 200 octets par clé en 440×280).

### Gaps
- Je n'ai pas mesuré `scipy.signal.convolve2d` (scipy n'est pas installé dans le bac à sable), ni le coût de l'affichage Tkinter (`Canvas.itemconfig` contre `PhotoImage.put`).
- Je ne sais pas si le sujet de NSI autorise numpy ; l'entier géant n'utilise que la bibliothèque standard.
- La version torique de l'entier géant n'a pas été mesurée.

## 8. Ordres de grandeur téléphone et ordinateur : générations par seconde atteignables pour 200×200 à 2000×2000

### Takeaway
Je n'ai trouvé aucun banc d'essai publié du jeu de la vie sur téléphone. Les comparaisons de processeurs disponibles suggèrent qu'un téléphone Android moyen est plusieurs fois plus lent qu'un ordinateur en JavaScript sur un seul thread : jusqu'à environ 10 fois entre un Galaxy A21s et un iPhone 13 (extrait de recherche). En appliquant un facteur de 3 à 10 aux mesures locales, un damier de 2000×2000 en bits donnerait environ 4 à 15 ms par génération sur un téléphone moyen, soit 60 images/s possibles avec 1 génération par image si l'affichage est bien fait. En 1 octet par cellule, on n'aurait qu'environ 6 à 20 gén/s. En objets, ce serait inutilisable.

### Cited Findings
- Selon Theodo (scores Geekbench), un Galaxy A21s a environ un dixième du score sur un cœur d'un iPhone 13, ce qui se traduit par du JavaScript environ 10 fois plus lent. — [Theodo](https://apps.theodo.com/article/what-is-the-performance-of-your-users-devices) **(extrait de recherche)**
- Les scores sur un cœur des Moto E14 et Galaxy A24 (4G) seraient inférieurs à celui d'un iPhone 6. — [Catchmetrics](https://catchmetrics.io/blog/understanding-the-impact-of-low-end-android-devices-on-web-performance) **(extrait de recherche)**
- L'iPhone 16 Pro obtiendrait environ 60 % de plus que le Galaxy S24 Ultra au score CPU de Geekbench (« performance inequality gap »). — [Web Performance Calendar](https://calendar.perfplanet.com/?p=2890) **(extrait de recherche)**
- Référence ordinateur publiée : 0,34 ns par cellule en JS, avec 4 workers, sur un i5-7600K à 4,4 GHz. — [Jumbub/game-of-life-js](https://github.com/Jumbub/game-of-life-js)
- Référence locale : moteur en bits sur un seul thread, 0,31 à 0,36 ns par cellule (Xeon à 2,1 GHz, Node 22). — *Mesure locale* (`life_js.js`)

### Inferences
- **Estimation pour un téléphone moyen**, en appliquant un facteur ×3 à ×10 aux mesures locales (**non vérifié, à mesurer sur l'appareil**) :

  | Plateau | Bits (0,3 ns/cellule en local) | Octets + sommes glissantes (4 ns) | Objets (20 à 50 ns) |
  |---|---|---|---|
  | 200×200 (40 000 cellules) | moins de 0,15 ms | 0,5 à 1,6 ms | 2,5 à 20 ms |
  | 1000×1000 | 1 à 3 ms | 12 à 40 ms | 0,06 à 0,5 s, et environ 240 Mo |
  | 2000×2000 | 4 à 12 ms | 50 à 160 ms | inutilisable (environ 1 Go) |
  | 4000×4000 | 15 à 50 ms | 0,2 à 0,6 s | inutilisable |

- **Budget d'une image** : 16,7 ms à 60 images/s. Le calcul en bits de 2000² (4 à 12 ms estimés) plus un affichage réduit de la partie visible (quelques ms) tient de justesse dans une image. Il faut donc séparer la cadence de calcul (générations par seconde, réglable) de la cadence d'affichage, et laisser le moteur sauter des images au lieu de bloquer.
- **Mesurer sur place** : intégrer dans la page un mini banc d'essai (par exemple 50 générations au démarrage) pour choisir automatiquement le nombre de générations par image, ou réduire la taille par défaut si l'appareil est lent.

### Gaps
- Aucune mesure réelle de JS sur iPhone ou sur Android de milieu de gamme n'a été trouvée pour ce type de calcul. Le facteur ×3 à ×10 est une extrapolation à partir de scores Geekbench sur un cœur cités de seconde main.
- Le surcoût éventuel du JIT de Safari (JavaScriptCore) par rapport à V8 sur ce noyau bit à bit n'est pas connu.
