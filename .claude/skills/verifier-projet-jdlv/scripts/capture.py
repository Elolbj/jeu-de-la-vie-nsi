"""
Ouvre la fenêtre du jeu (Jdlv_IHM), fait tourner le canon de Gosper puis
enregistre une capture d'écran.

Usage (il faut un écran ; sur un serveur, passer par xvfb-run) :
    xvfb-run -a -s "-screen 0 1280x800x24" python capture.py <projet> <image.png>
"""

import subprocess
import sys

dossier, image = sys.argv[1], sys.argv[2]
sys.path.insert(0, dossier)

from jdlv import Jdlv          # noqa: E402  (import après sys.path)
from jdlv_ihm import Jdlv_IHM  # noqa: E402
from motifs import MOTIFS      # noqa: E402

jeu = Jdlv(70, 45, torique=False)
jeu.placer_motif(MOTIFS["Canon de Gosper"], 2, 2)
ihm = Jdlv_IHM(jeu)
ihm.vitesse.set(60)


def capturer():
    """Prend la capture (ImageMagick) puis ferme la fenêtre."""
    ihm.arreter()
    ihm.fenetre.update()
    subprocess.run(["import", "-window", "root", image], check=True)
    print(f"capture : {image} (tour {jeu.tour}, population {jeu.population()})")
    ihm.fenetre.destroy()


ihm.fenetre.after(200, ihm.demarrer)
ihm.fenetre.after(2500, capturer)
ihm.lancer()
