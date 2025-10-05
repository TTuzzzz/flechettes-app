import Reglement as coeur
import streamlit as st
# =========================
# APP STREAMLIT
# =========================
st.set_page_config(
    page_title="Documentation",
    page_icon="🎯",
)
st.title("🎯 Fléchettes Reference")

# =========================
# Présentation du système Elo
# =========================

st.markdown("""
## ℹ️ Exemple détaillé du calcul Elo

Imaginons une partie de fléchettes avec **3 équipes** :

- **Équipe 1** : Tom (Elo 1200) et Marouane (Elo 1250)  
- **Équipe 2** : Vincent (Elo 1400)  
- **Équipe 3** : Yann (Elo 1150) et Xavier (Elo 900)  

Classement final de la partie :  
🥇 1er : **Tom et Marouane**  
🥈 2ème : **Vincent**  
🥉 3ème : **Yann et Xavier**  

Facteur de mise à jour choisi : **K = 24**

---

### Étape 1 : Calculer la force de chaque équipe
Pour comparer des équipes, on prend la **moyenne de l’Elo** de leurs joueurs :

- Tom et Marouane : (1200 + 1250) / 2 = **1225**  
- Vincent : (1400) = **1400**  
- Yann et Xavier : (1150 + 900) / 2 = **1025**

---

### Étape 2 : Probabilité de gagner contre une autre équipe
On calcule la probabilité qu’une équipe *i* batte une équipe *j* avec la formule Elo :

$$
E_{i,j} = \\frac{1}{1 + 10^{\\frac{R_i - R_j}{400}}}
$$

Exemple :  
- Pour **Tom et Marouane** contre **Vincent** :  
$E_{1,2} = \\frac{1}{1 + 10^{(1225 - 1400)/400}} ≈ 0.27$  
→ donc **Tom et Marouane** ont **27% de chance** de battre Vincent.  

- Pour **Tom et Marouane** contre **Yann et Xavier** :  
$E_{1,3} = \\frac{1}{1 + 10^{(1225 - 1025)/400}} ≈ 0.76$  
→ donc **Tom et Marouane** ont **76% de chance** de battre Yann et Xavier.  

On répète pour toutes les équipes, puis on prend la **moyenne** pour obtenir l’attente globale de chaque équipe :

- **Tom et Marouane** : (0.27 + 0.76) / 2 = **0.52**  
- **Vincent** : (0.73 + 0.90) / 2 = **0.81**  
- **Yann et Xavier** : (0.24 + 0.10) / 2 = **0.17**

---

### Étape 3 : Score réel en fonction du classement final
Le classement est transformé en score entre 0 et 1 :  

$$
S_i = \\frac{n - \\text{rang}(i)}{n - 1}
$$

Avec 3 équipes :  
- 1ère place → $S = 1$  
- 2ème place → $S = 0.5$  
- 3ème place → $S = 0$

---

### Étape 4 : Variation d’Elo des équipes
La formule finale est :

$$
\\Delta R = K \\cdot (S - E)
$$

- Équipe 1 : ΔR = 24 × (1 - 0.51) = **+12**  
- Équipe 2 : ΔR = 24 × (0.5 - 0.81) = **-8**  
- Équipe 3 : ΔR = 24 × (0 - 0.17) = **-4**

---

### Étape 5 : Répartition entre les joueurs
Chaque variation est partagée **équitablement** entre les joueurs de l’équipe :

- **Équipe 1 (+12 au total, 2 joueurs)**  
  - Tom : 1200 + 6 = **1206**  
  - Marouane : 1250 + 6 = **1256**

- **Équipe 2 (-8 au total, 1 joueur)**  
  - Vincent : 1400 - 8 = **1392**

- **Équipe 3 (-4 au total, 2 joueurs)**  
  - Yann : 1150 - 2 = **1148**  
  - Xavier : 900 - 2 = **898**

La somme des variations est toujours **0** : ce que certains gagnent, les autres le perdent.  
C’est le principe fondamental du classement Elo ✅

---
""")
# Init DB
#coeur.init_db()

# Charger joueurs
players = coeur.get_players()