import streamlit as st
import pandas as pd

st.set_page_config(page_title="Cockpit de Performance Hybride", layout="wide")
st.title("Optimiseur de 1RM & Repos")
st.write("Priorisation basée sur le volume et l'objectif")

# --- INPUTS ---
col1, col2 = st.columns(2)
with col1:
    poids = st.number_input("Poids soulevé (kg)", value=100.0, step=2.5)
with col2:
    reps = st.slider("Nombre de répétitions effectuées", 1, 20, 5)

# --- TABLE DE BERGER (1961) — pourcentage du 1RM selon les reps ---
berger_table = {
    1:  100.0,
    2:  95.5,
    3:  92.2,
    4:  88.9,
    5:  85.6,
    6:  83.1,
    7:  79.8,
    8:  77.3,
    9:  76.0,
    10: 74.4,
    11: 73.4,
    12: 71.0,
    13: 69.4,
    14: 67.8,
    15: 66.2,
    16: 63.6,
    17: 62.0,
    18: 60.4,
    19: 58.8,
    20: 56.0,
}

pct_berger = berger_table.get(reps, None)
f_berger = (poids * 100) / pct_berger if pct_berger else None

# --- CALCULS DES 7 FORMULES ---
f_brzycki  = poids / (1.0278 - 0.0278 * reps) if reps < 37 else 0
f_epley    = poids * (1 + reps / 30)
f_lander   = (100 * poids) / (101.3 - 2.67123 * reps)
f_lombardi = poids * (reps ** 0.1)
f_mayhew   = (100 * poids) / (52.2 + 41.9 * (2.718 ** (-0.055 * reps)))
f_oconner  = poids * (1 + 0.025 * reps)
f_wathan   = (100 * poids) / (48.8 + 53.8 * (2.718 ** (-0.075 * reps)))

all_formulas = [f_epley, f_brzycki, f_lander, f_lombardi, f_mayhew, f_oconner, f_wathan]
moyenne_7 = sum(all_formulas) / 7
moyenne_3 = (f_brzycki + f_epley + f_wathan) / 3

# --- CALCUL PRINCIPAL ---
if reps == 1:
    rm_final = poids
    methode_nom = "Poids direct (1 rep = 1RM)"
    formule_recommandee = "Mesure directe"
    niveau_fiabilite = "success"

elif 2 <= reps <= 10:
    facteur = 0.995 if reps <= 5 else 1.00
    rm_final = moyenne_3 * facteur
    methode_nom = "Brzycki + Epley + Wathan (2–10 reps)"
    formule_recommandee = "✅ Brzycki (la plus précise sur cette plage)"
    niveau_fiabilite = "success"

elif 11 <= reps <= 15:
    # Lombardi prioritaire, pondéré avec Berger
    if f_berger:
        rm_base = f_lombardi * 0.6 + f_berger * 0.4
    else:
        rm_base = f_lombardi
    rm_final = rm_base * 0.965
    methode_nom = "Lombardi (priorité) + Berger — séries longues (11–15 reps)"
    formule_recommandee = "⚠️ Lombardi (priorité Fit'Distance >10 reps) — précision modérée"
    niveau_fiabilite = "warning"

else:
    if f_berger:
        rm_base = f_lombardi * 0.55 + f_berger * 0.45
    else:
        rm_base = f_lombardi
    rm_final = rm_base * 0.945
    methode_nom = "Lombardi (priorité) + Berger — très longues séries (>15 reps)"
    formule_recommandee = "⚠️ Lombardi + Berger — fiabilité limitée au-delà de 15 reps"
    niveau_fiabilite = "error"

# --- MÉTRIQUES PRINCIPALES ---
st.divider()
c1, c2, c3 = st.columns(3)
with c1:
    st.metric("🎯 1RM estimé", f"{round(rm_final, 1)} kg")
    st.caption(f"Méthode : {methode_nom}")
with c2:
    st.metric("📊 Moyenne 7 formules", f"{round(moyenne_7, 1)} kg")
with c3:
    if f_berger:
        st.metric("📋 Table de Berger", f"{round(f_berger, 1)} kg",
                  help=f"{reps} reps = {pct_berger}% du 1RM selon Berger (1961)")
    else:
        st.metric("📐 Moyenne 3 formules", f"{round(moyenne_3, 1)} kg")

msg = f"**Formule recommandée pour {reps} reps :** {formule_recommandee}"
if niveau_fiabilite == "success":
    st.success(msg)
elif niveau_fiabilite == "warning":
    st.warning(msg)
else:
    st.error(msg)

# --- TABLE DE BERGER COMPLÈTE ---
st.divider()
st.subheader("📋 Table de Berger (1961) — correspondance reps / % 1RM")

if pct_berger:
    st.info(
        f"🔎 Pour **{reps} répétitions**, vous travaillez à **{pct_berger}%** de votre 1RM "
        f"selon Berger → 1RM estimé = **{round(f_berger, 1)} kg**"
    )

couleurs_berger = {
    "Force Max / Force": ("#fff0f0", "#ff4b4b"),
    "Hypertrophie":      ("#f0fff4", "#21c354"),
    "Endurance":         ("#f5f5f5", "#888888"),
}

html_b = """
<style>
  .btable { width: 100%; border-collapse: collapse; font-size: 14px; }
  .btable th { background-color: #262730; color: white; padding: 8px 12px; text-align: left; }
  .btable td { padding: 7px 12px; border-bottom: 1px solid #ddd; }
</style>
<table class="btable">
  <tr><th>Reps</th><th>% 1RM (Berger)</th><th>1RM estimé (kg)</th><th>Zone</th></tr>
"""

for r, pct in berger_table.items():
    charge_b = round((poids * 100) / pct, 1)
    if r <= 6:
        zone = "Force Max / Force"
    elif r <= 12:
        zone = "Hypertrophie"
    else:
        zone = "Endurance"
    bg, fg = couleurs_berger[zone]
    actif = r == reps
    fw = "bold" if actif else "normal"
    bl = f"border-left: 4px solid {fg};" if actif else ""
    indicateur = "👉 " if actif else ""
    html_b += f"""
  <tr style="background-color:{bg}; font-weight:{fw}; {bl}">
    <td>{indicateur}{r}</td>
    <td style="color:{fg};">{pct}%</td>
    <td><b>{charge_b} kg</b></td>
    <td style="color:{fg};">{zone}</td>
  </tr>
"""

html_b += "</table>"
st.markdown(html_b, unsafe_allow_html=True)

# --- TABLEAU DE PROGRAMMATION ---
st.divider()
st.subheader("🗓️ Tableau de programmation")

paliers = [
    (1.00, "Force Max",    "3 – 5 min",      "🔴", "#ff4b4b", "#fff0f0"),
    (0.95, "Force Max",    "3 – 5 min",      "🔴", "#ff4b4b", "#fff0f0"),
    (0.90, "Force",        "3 – 5 min",      "🟠", "#ff8800", "#fff5e6"),
    (0.85, "Force",        "2 – 3 min",      "🟠", "#ff8800", "#fff5e6"),
    (0.80, "Hypertrophie", "90 sec – 2 min", "🟢", "#21c354", "#f0fff4"),
    (0.75, "Hypertrophie", "1 – 2 min",      "🟢", "#21c354", "#f0fff4"),
    (0.70, "Hypertrophie", "1 – 2 min",      "🟢", "#21c354", "#f0fff4"),
    (0.65, "Endurance",    "30 – 60 sec",    "⚪", "#888888", "#f5f5f5"),
    (0.60, "Endurance",    "30 – 60 sec",    "⚪", "#888888", "#f5f5f5"),
    (0.50, "Endurance",    "30 – 60 sec",    "⚪", "#888888", "#f5f5f5"),
]

# Reps théoriques selon la table de Berger (inversion du tableau)
# On cherche pour chaque % la valeur de reps la plus proche dans berger_table
def reps_pour_pct(pct_cible):
    meilleur_r, meilleure_diff = 1, 999
    for r, pct in berger_table.items():
        diff = abs(pct - pct_cible * 100)
        if diff < meilleure_diff:
            meilleure_diff, meilleur_r = diff, r
    return meilleur_r

reps_prog = {pct: reps_pour_pct(pct) for pct, *_ in paliers}

html_prog = """
<style>
  .ptable { width: 100%; border-collapse: collapse; font-size: 15px; }
  .ptable th { background-color: #262730; color: white; padding: 10px 14px; text-align: left; }
  .ptable td { padding: 9px 14px; border-bottom: 1px solid #ddd; }
</style>
<table class="ptable">
  <tr><th>%</th><th>Objectif</th><th>Charge (kg)</th><th>Reps théoriques (Berger)</th><th>Repos suggéré</th></tr>
"""

for pct, label, repos, emoji, color_fg, color_bg in paliers:
    charge = round(rm_final * pct, 1)
    r_th = reps_prog[pct]
    html_prog += f"""
  <tr style="background-color:{color_bg}; color:#111;">
    <td><b style="color:{color_fg};">{int(pct*100)}%</b></td>
    <td>{emoji} <b style="color:{color_fg};">{label}</b></td>
    <td><b>{charge} kg</b></td>
    <td>~{r_th} reps</td>
    <td>{repos}</td>
  </tr>
"""

html_prog += "</table>"
st.markdown(html_prog, unsafe_allow_html=True)

st.markdown("""
<br><small>
🔴 <b>Force Max</b> (95–100%) &nbsp;|&nbsp;
🟠 <b>Force</b> (85–90%) &nbsp;|&nbsp;
🟢 <b>Hypertrophie</b> (70–80%) &nbsp;|&nbsp;
⚪ <b>Endurance</b> (50–65%)
&nbsp;&nbsp;— Reps théoriques calculées depuis la table de Berger (1961)
</small>
""", unsafe_allow_html=True)

# --- COMPARATIF DES 7 FORMULES + BERGER ---
st.divider()
with st.expander("📊 Comparatif des 7 formules + Berger"):
    noms    = ["Epley", "Brzycki", "Lander", "Lombardi", "Mayhew", "O'Conner", "Wathan", "Berger"]
    valeurs = [round(v, 1) for v in all_formulas] + [round(f_berger, 1) if f_berger else 0]

    if reps <= 10:
        formules_top = ["Brzycki", "Epley", "Wathan", "Berger"]
    elif reps <= 15:
        formules_top = ["Lombardi", "Berger"]
    else:
        formules_top = ["Lombardi", "Berger"]

    df_f = pd.DataFrame({"Formule": noms, "1RM estimé (kg)": valeurs})
    df_f["Recommandée ?"] = df_f["Formule"].apply(lambda x: "⭐ Oui" if x in formules_top else "—")
    st.dataframe(df_f, use_container_width=True, hide_index=True)
    st.caption(f"📌 Pour {reps} reps, les formules ⭐ sont les plus fiables selon la littérature.")

# --- FORMULES MATHÉMATIQUES ---
with st.expander("📐 Détail des formules scientifiques"):
    st.latex(r"Berger~(1961): 1RM = \frac{Poids \times 100}{\%1RM_{table}}")
    st.latex(r"Lombardi: 1RM = Poids \times Reps^{0.1}")
    st.latex(r"Brzycki: 1RM = \frac{Poids}{1.0278 - 0.0278 \times Reps}")
    st.latex(r"Epley: 1RM = Poids \times \left(1 + \frac{Reps}{30}\right)")
    st.latex(r"Lander: 1RM = \frac{100 \times Poids}{101.3 - 2.67123 \times Reps}")
    st.latex(r"Wathan: 1RM = \frac{100 \times Poids}{48.8 + 53.8 \times e^{-0.075 \times Reps}}")
    st.latex(r"Mayhew: 1RM = \frac{100 \times Poids}{52.2 + 41.9 \times e^{-0.055 \times Reps}}")
    st.latex(r"O'Conner: 1RM = Poids \times (1 + 0.025 \times Reps)")
    st.info(
        "**Stratégie de calcul :**\n\n"
        "- **1 rep** : mesure directe.\n"
        "- **2–10 reps** : moyenne de Brzycki + Epley + Wathan.\n"
        "- **11–20 reps** : **Lombardi prioritaire**, pondéré avec "
        "la table de Berger pour corriger les surestimations.\n\n"
        "Les reps théoriques du tableau de programmation sont issues de la **table de Berger (1961)**."
    )