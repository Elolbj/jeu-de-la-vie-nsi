/*
 * Teste la version web du jeu de la vie (web/jeu_de_la_vie.html).
 *
 * Usage : node tester_web.js <dossier_du_projet>
 *  1. Moteur : le Jdlv JavaScript est comparé, tour après tour, à un calcul
 *     de référence indépendant (tableaux aléatoires, bords fermés et tore),
 *     puis à des valeurs connues (diehard, pentadécathlon).
 *  2. Navigateur (si Playwright est installé) : page ouverte sur un iPhone
 *     simulé, sans erreur JavaScript, sans défilement horizontal, animation
 *     qui avance, damier de 2 000 x 2 000 cases chronométré.
 * Code de sortie 0 si tout passe.
 */
const fs = require("fs");
const path = require("path");

const projet = path.resolve(process.argv[2] || ".");
const page_html = path.join(projet, "web", "jeu_de_la_vie.html");
let echecs = 0;
const bilan = (ok, message) => { console.log(`  [${ok ? "OK" : "ÉCHEC"}] ${message}`); if (!ok) echecs++; };

// ---------------------------------------------------------------- 1. Moteur
console.log("== Moteur JavaScript");
const html = fs.readFileSync(page_html, "utf8");
const script = html.split("<script>")[1].split("// ------------------------------------------------------------- jdlv_ihm.py")[0];
const M = new Function(script + "; return { Jdlv, MOTIFS };")();

function reference(vivantes, W, H, tore) {
  const compte = new Map();
  for (const k of vivantes) {
    const x = k % W, y = (k - x) / W;
    for (let dy = -1; dy <= 1; dy++) for (let dx = -1; dx <= 1; dx++) {
      if (!dx && !dy) continue;
      let vx = x + dx, vy = y + dy;
      if (tore) { vx = (vx + W) % W; vy = (vy + H) % H; } else if (vx < 0 || vx >= W || vy < 0 || vy >= H) continue;
      const j = vy * W + vx;
      compte.set(j, (compte.get(j) || 0) + 1);
    }
  }
  const resultat = new Set();
  for (const [j, n] of compte) if (n === 3 || (n === 2 && vivantes.has(j))) resultat.add(j);
  return resultat;
}
const vivantes = (jeu) => { const s = new Set(); for (let i = 0; i < jeu.largeur * jeu.hauteur; i++) if (jeu.grille[i]) s.add(i); return s; };

let accord = true;
for (const tore of [true, false]) for (const [W, H] of [[23, 17], [3, 3], [64, 9]]) {
  const jeu = new M.Jdlv(W, H, tore);
  jeu.remplir_aleatoirement(0.35);
  let attendu = vivantes(jeu);
  for (let t = 0; t < 50 && accord; t++) {
    jeu.tour_suivant();
    attendu = reference(attendu, W, H, tore);
    const obtenu = vivantes(jeu);
    if (obtenu.size !== attendu.size || [...obtenu].some((k) => !attendu.has(k)) || jeu.population() !== obtenu.size) accord = false;
  }
}
bilan(accord, "même résultat que le calcul de référence (300 tours, tore et bords fermés)");
const jusqu_a_la_fin = (jeu) => { while (jeu.statut === "en évolution" && jeu.tour < 1000) jeu.tour_suivant(); return jeu; };
let jeu = new M.Jdlv(40, 40, false); jeu.charger_motif(M.MOTIFS["Diehard"]); jusqu_a_la_fin(jeu);
bilan(jeu.statut === "extinction" && jeu.tour === 130, `diehard éteint au tour 130 (obtenu : ${jeu.tour})`);
jeu = new M.Jdlv(30, 20, false); jeu.charger_motif(M.MOTIFS["Pentadécathlon"]); jusqu_a_la_fin(jeu);
bilan(jeu.periode === 15, `pentadécathlon de période 15 (obtenu : ${jeu.periode})`);
const geant = new M.Jdlv(2000, 2000, true); geant.remplir_aleatoirement(0.3);
let debut = Date.now(); for (let t = 0; t < 5; t++) geant.tour_suivant();
const ms = (Date.now() - debut) / 5;
bilan(ms < 400, `2 000 × 2 000 cases : ${ms.toFixed(0)} ms par tour (calcul seul)`);

// ------------------------------------------------------------ 2. Navigateur
(async () => {
  let playwright;
  try { playwright = require("playwright"); } catch { console.log("== Navigateur : Playwright absent, partie ignorée"); return; }
  console.log("== Navigateur (iPhone simulé)");
  const navigateur = await playwright.chromium.launch();
  try {
    const page = await navigateur.newPage({ ...playwright.devices["iPhone 13"] });
    const erreurs = [];
    page.on("pageerror", (e) => erreurs.push(e.message));
    page.on("console", (m) => { if (m.type() === "error") erreurs.push(m.text()); });
    await page.goto("file://" + page_html);
    await page.waitForTimeout(600);
    const largeurs = await page.evaluate(() => [document.documentElement.scrollWidth, innerWidth]);
    bilan(largeurs[0] <= largeurs[1], `pas de défilement horizontal (${largeurs[0]} px pour ${largeurs[1]} px)`);
    await page.tap("#b-lecture"); await page.waitForTimeout(1000); await page.tap("#b-lecture");
    const tour = Number((await page.textContent("#stat-tour")).replace(/\s/g, ""));
    bilan(tour > 0, `l'animation avance (tour ${tour} après 1 s)`);
    await page.tap("#b-reglages");
    await page.selectOption("#taille-damier", "2000x2000");
    await page.tap("#b-fermer"); await page.tap("#b-hasard");
    const duree = await page.evaluate(() => { const d = performance.now(); for (let i = 0; i < 3; i++) document.getElementById("b-suivant").click(); return (performance.now() - d) / 3; });
    bilan(duree < 600, `damier 2 000 × 2 000 dans la page : ${duree.toFixed(0)} ms par tour avec le dessin`);
    if (process.argv[3]) { await page.screenshot({ path: process.argv[3] }); console.log(`  capture : ${process.argv[3]}`); }
    bilan(erreurs.length === 0, erreurs.length ? `erreurs JavaScript : ${erreurs.join(" | ")}` : "aucune erreur JavaScript");
  } finally {
    await navigateur.close();
  }
})().then(() => {
  console.log(`\nRésultat : ${echecs ? `${echecs} vérification(s) en échec` : "version web conforme"}`);
  process.exit(echecs ? 1 : 0);
});
