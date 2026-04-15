import streamlit as st
import pandas as pd
import math

st.set_page_config(page_title="Cockpit de Performance Hybride", layout="wide")
st.title("Optimiseur de 1RM & Repos")
st.write("Priorisation basée sur le volume et l'objectif")

# --- INPUTS ---
col1, col2 = st.columns(2)
with col1:
    poids = st.number_input("Poids soulevé (kg)", value=100.0, step=2.5)
with col2:
    reps = st.slider("Nombre de répétitions effectuées", 1, 20, 5)

# --- TABLE DE BERGER (1961) ---
berger_table = {
    1: 100.0, 2: 95.5, 3: 92.2, 4: 88.9, 5: 85.6,
    6: 83.1,  7: 79.8, 8: 77.3, 9: 76.0, 10: 74.4,
    11: 73.4, 12: 71.0, 13: 69.4, 14: 67.8, 15: 66.2,
    16: 63.6, 17: 62.0, 18: 60.4, 19: 58.8, 20: 56.0,
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

# =============================================================================
# SECTION RIR — RÉPÉTITIONS EN RÉSERVE
# =============================================================================
st.divider()
st.subheader("RIR — Répétitions In Reserve")

st.markdown("""
Le RIR (Reps In Reserve) indique combien de répétitions supplémentaires
vous pourriez encore effectuer avant l'échec musculaire. Il est directement lié
au RPE (Rate of Perceived Exertion, échelle de 1 à 10).
""")

# Tableau RIR par % de 1RM — basé sur la correspondance Zourdos et al. (2016)
rir_table = {
    100: (0,  10, "Effort maximal absolu — échec imminent"),
    97:  (1,  9.5,"1 rep en réserve — effort quasi-maximal"),
    95:  (1,  9,  "1 rep en réserve — effort très élevé"),
    92:  (2,  8.5,"2 reps en réserve — charge lourde"),
    90:  (2,  8,  "2–3 reps en réserve — zone de force"),
    87:  (3,  7.5,"3 reps en réserve — intensité élevée"),
    85:  (3,  7,  "3–4 reps en réserve — zone de force-hypertrophie"),
    82:  (4,  6.5,"4 reps en réserve — stimulus hypertrophique élevé"),
    80:  (4,  6,  "4–5 reps en réserve — zone hypertrophie optimale"),
    77:  (5,  5.5,"5 reps en réserve — charge modérée"),
    75:  (5,  5,  "5–6 reps en réserve — hypertrophie / endurance"),
    70:  (6,  4,  "6+ reps en réserve — charge légère"),
    65:  (8,  3,  "8+ reps en réserve — travail d'endurance"),
    60:  (10, 2,  "10+ reps en réserve — échauffement / activation"),
    50:  (15, 1,  "Charge très légère — récupération active"),
}

# Calcul du RIR pour la série actuelle
pct_actuel = round((poids / rm_final) * 100) if rm_final > 0 else 0

def get_rir_info(pct):
    """Retourne les infos RIR pour un % donné du 1RM."""
    paliers_tries = sorted(rir_table.keys(), reverse=True)
    for p in paliers_tries:
        if pct >= p:
            return rir_table[p]
    return rir_table[50]

rir_val, rpe_val, rir_desc = get_rir_info(pct_actuel)

col_rir1, col_rir2, col_rir3 = st.columns(3)
with col_rir1:
    st.metric("📊 % du 1RM (série actuelle)", f"{pct_actuel}%")
with col_rir2:
    st.metric("🔋 RIR estimé", f"~{rir_val} reps",
              help="Nombre de répétitions encore réalisables avant l'échec musculaire")
with col_rir3:
    st.metric("💢 RPE estimé", f"{rpe_val}/10",
              help="Rate of Perceived Exertion — 10 = échec musculaire")

st.info(f"**{rir_desc}**")

# Tableau RIR complet pour tous les % du 1RM
with st.expander("📋 Tableau complet RIR / RPE par % du 1RM"):
    rir_rows = []
    for p in sorted(rir_table.keys(), reverse=True):
        rv, rpev, desc = rir_table[p]
        charge_kg = round(rm_final * p / 100, 1)
        if p >= 90:
            zone = "Force Max"
        elif p >= 80:
            zone = "Force"
        elif p >= 65:
            zone = "Hypertrophie"
        else:
            zone = "Endurance"
        rir_rows.append({
            "% 1RM": f"{p}%",
            "Charge (kg)": f"{charge_kg} kg",
            "RIR": f"~{rv}",
            "RPE": f"{rpev}/10",
            "Zone": zone,
            "Description": desc,
        })
    df_rir = pd.DataFrame(rir_rows)
    st.dataframe(df_rir, use_container_width=True, hide_index=True)

# =============================================================================
# SECTION TEMPO
# =============================================================================
st.divider()
st.subheader("Conseils de Tempo par Objectif")

st.markdown("""
Le **tempo** se note en 4 chiffres : **Excentrique – Pause bas – Concentrique – Pause haut**.
Par exemple **3-1-X-0** signifie : 3s de descente · 1s de pause en bas · Explosion · 0s de pause en haut.
""")

# Données de tempo par objectif
tempo_data = {
    "Force Max": {
        "emoji": "🔴",
        "tempo": "3 – 1 – X – 1",
        "excentrique": "3s",
        "pause_bas": "1s",
        "concentrique": "X (explosion maximale)",
        "pause_haut": "1s",
        "charge_pct": "90–100%",
        "series": "3–5",
        "reps_range": "1–3",
        "intention": "Recruter un maximum d'unités motrices. Phase concentrique explosive même avec charge lourde.",
        "conseil": "Ne jamais sacrifier la technique pour la vitesse. L'intention explosive compte plus que la vitesse réelle."
    },
    "Force": {
        "emoji": "🟠",
        "tempo": "3 – 1 – 2 – 1",
        "excentrique": "3s",
        "pause_bas": "1s",
        "concentrique": "2s (contrôlé mais puissant)",
        "pause_haut": "1s",
        "charge_pct": "80–90%",
        "series": "4–5",
        "reps_range": "3–6",
        "intention": "Développer la force fonctionnelle avec contrôle complet du mouvement.",
        "conseil": "La pause en bas élimine le rebond et augmente la tension musculaire réelle."
    },
    "Hypertrophie": {
        "emoji": "🟢",
        "tempo": "3 – 1 – 2 – 0",
        "excentrique": "3–4s",
        "pause_bas": "1s",
        "concentrique": "2s (contrôlé)",
        "pause_haut": "0s (tension continue)",
        "charge_pct": "65–80%",
        "series": "3–4",
        "reps_range": "8–12",
        "intention": "Maximiser le temps sous tension (TUT). Pas de repos en haut pour maintenir la tension musculaire.",
        "conseil": "Le TUT cible : 40–70 secondes par série. Concentrez-vous sur la sensation musculaire plutôt que sur le poids."
    },
    "Endurance-Force": {
        "emoji": "🔵",
        "tempo": "2 – 0 – 2 – 0",
        "excentrique": "2s",
        "pause_bas": "0s",
        "concentrique": "2s",
        "pause_haut": "0s (mouvement fluide)",
        "charge_pct": "50–65%",
        "series": "3–4",
        "reps_range": "15–20+",
        "intention": "Développer la résistance musculaire et l'efficacité métabolique.",
        "conseil": "Le rythme régulier favorise la récupération intra-série. Idéal pour les circuits ou le cardio-musculaire."
    },
    "Puissance / Explosivité": {
        "emoji": "⚡",
        "tempo": "2 – 0 – X – 1",
        "excentrique": "2s (rapide mais contrôlé)",
        "pause_bas": "0s (rebond amorti)",
        "concentrique": "X (vitesse maximale)",
        "pause_haut": "1s",
        "charge_pct": "30–60%",
        "series": "4–6",
        "reps_range": "3–6",
        "intention": "Développer la puissance maximale (force × vitesse). Utilisé pour les sports explosifs.",
        "conseil": "Charge légère = vitesse maximale. Si la barre ralentit, réduisez la charge de 5–10%."
    },
    "Activation / Échauffement": {
        "emoji": "🟡",
        "tempo": "2 – 1 – 2 – 1",
        "excentrique": "2s",
        "pause_bas": "1s",
        "concentrique": "2s",
        "pause_haut": "1s",
        "charge_pct": "40–50%",
        "series": "2–3",
        "reps_range": "8–12",
        "intention": "Activer les muscles, lubrifier les articulations, préparer le système nerveux.",
        "conseil": "Idéal en début de séance. Accent sur la qualité du mouvement, pas sur l'effort."
    },
}

# Onglets par objectif
tabs = st.tabs([f"{v['emoji']} {k}" for k, v in tempo_data.items()])

for tab, (objectif, data) in zip(tabs, tempo_data.items()):
    with tab:
        col_t1, col_t2 = st.columns([1, 1])
        with col_t1:
            st.markdown(f"### Tempo : `{data['tempo']}`")
            html_tempo = f"""
<style>
  .tempo-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-top: 12px; }}
  .tempo-box {{ background: #f8f9fa; border-radius: 8px; padding: 12px; border-left: 4px solid #888; }}
  .tempo-box.exc {{ border-color: #ff4b4b; }}
  .tempo-box.pause {{ border-color: #ff8800; }}
  .tempo-box.conc {{ border-color: #21c354; }}
  .tempo-box.top {{ border-color: #888; }}
  .tempo-label {{ font-size: 11px; color: #888; text-transform: uppercase; font-weight: 600; }}
  .tempo-val {{ font-size: 18px; font-weight: bold; margin: 4px 0 2px; }}
  .tempo-name {{ font-size: 12px; color: #555; }}
</style>
<div class="tempo-grid">
  <div class="tempo-box exc">
    <div class="tempo-label">① Excentrique (descente)</div>
    <div class="tempo-val">{data['excentrique']}</div>
    <div class="tempo-name">Phase de freinage / allongement</div>
  </div>
  <div class="tempo-box pause">
    <div class="tempo-label">② Pause en bas (transition)</div>
    <div class="tempo-val">{data['pause_bas']}</div>
    <div class="tempo-name">Élimination du rebond</div>
  </div>
  <div class="tempo-box conc">
    <div class="tempo-label">③ Concentrique (poussée/traction)</div>
    <div class="tempo-val">{data['concentrique']}</div>
    <div class="tempo-name">Phase de force / raccourcissement</div>
  </div>
  <div class="tempo-box top">
    <div class="tempo-label">④ Pause en haut</div>
    <div class="tempo-val">{data['pause_haut']}</div>
    <div class="tempo-name">Transition / récupération partielle</div>
  </div>
</div>
"""
            st.markdown(html_tempo, unsafe_allow_html=True)

        with col_t2:
            charge_kg = round(rm_final * int(data['charge_pct'].split('–')[0].replace('%', '')) / 100, 1)
            charge_kg_max = round(rm_final * int(data['charge_pct'].split('–')[1].replace('%', '')) / 100, 1)
            st.markdown(f"**Charge recommandée** : {data['charge_pct']} du 1RM")
            st.markdown(f"→ Soit **{charge_kg} – {charge_kg_max} kg** pour votre 1RM de {round(rm_final,1)} kg")
            st.markdown(f"**Séries × Reps** : {data['series']} × {data['reps_range']}")

            # Calcul TUT
            try:
                exc_s = int(data['excentrique'].split('s')[0].split('–')[0].strip())
                pause_b = int(data['pause_bas'].replace('s', '').strip())
                conc_str = data['concentrique'].split('s')[0].strip()
                conc_s = 1 if conc_str == 'X' else int(conc_str.split('–')[0])
                pause_h = int(data['pause_haut'].split('s')[0].strip())
                reps_min = int(data['reps_range'].split('–')[0].strip().replace('+', ''))
                reps_max_str = data['reps_range'].split('–')[-1].strip().replace('+', '')
                reps_max = int(reps_max_str) if reps_max_str.isdigit() else reps_min + 4
                tut_min = (exc_s + pause_b + conc_s + pause_h) * reps_min
                tut_max = (exc_s + pause_b + conc_s + pause_h) * reps_max
                st.markdown(f"**TUT estimé** (Temps sous tension) : **{tut_min}–{tut_max} secondes** par série")
            except Exception:
                st.markdown("**TUT** : variable selon l'exécution")

            st.info(f"**Intention** : {data['intention']}")
            st.warning(f"💡 **Conseil** : {data['conseil']}")

# =============================================================================
# SECTION FATIGUE & RÉCUPÉRATION
# =============================================================================
st.divider()
st.subheader("Fatigue & Récupération Estimée")

st.markdown("""
Renseignez les paramètres de votre séance pour estimer la **dette de fatigue**
et le **temps de récupération recommandé** avant la prochaine séance sur le même groupe musculaire.
""")

col_f1, col_f2, col_f3 = st.columns(3)
with col_f1:
    nb_series = st.number_input("Nombre de séries effectuées", min_value=1, max_value=20, value=4)
with col_f2:
    groupe_musculaire = st.selectbox(
        "Groupe musculaire principal",
        ["Pectoraux", "Dos (grand dorsal)", "Épaules", "Quadriceps", "Ischio-jambiers",
         "Fessiers", "Biceps", "Triceps", "Mollets", "Abdominaux / Core"]
    )
with col_f3:
    experience = st.selectbox(
        "Niveau d'expérience",
        ["Débutant (< 1 an)", "Intermédiaire (1–3 ans)", "Avancé (3–5 ans)", "Expert (5 ans+)"]
    )

# Récupération de base par groupe musculaire (heures)
recup_base = {
    "Pectoraux": 48, "Dos (grand dorsal)": 48, "Épaules": 48,
    "Quadriceps": 72, "Ischio-jambiers": 72, "Fessiers": 72,
    "Biceps": 36, "Triceps": 36, "Mollets": 36, "Abdominaux / Core": 24
}

recup_heures_base = recup_base.get(groupe_musculaire, 48)

# Facteur intensité selon % du 1RM
if pct_actuel >= 90:
    facteur_intensite = 1.4
elif pct_actuel >= 80:
    facteur_intensite = 1.2
elif pct_actuel >= 70:
    facteur_intensite = 1.0
else:
    facteur_intensite = 0.8

# Facteur volume (séries)
facteur_volume = 1.0 + max(0, (nb_series - 4)) * 0.05

# Facteur expérience (les avancés récupèrent plus vite)
facteur_exp = {"Débutant (< 1 an)": 1.3, "Intermédiaire (1–3 ans)": 1.1,
               "Avancé (3–5 ans)": 0.9, "Expert (5 ans+)": 0.8}
fexp = facteur_exp.get(experience, 1.0)

recup_finale = recup_heures_base * facteur_intensite * facteur_volume * fexp
recup_finale = round(recup_finale)

# Volume total estimé (tonnage)
tonnage = round(poids * reps * nb_series, 0)

# Score de fatigue (0–10)
score_fatigue = min(10, round((pct_actuel / 100) * (nb_series / 5) * 10 * fexp, 1))

col_fat1, col_fat2, col_fat3 = st.columns(3)
with col_fat1:
    st.metric("⚡ Tonnage de la séance", f"{int(tonnage):,} kg".replace(",", " "))
with col_fat2:
    st.metric("💢 Score de fatigue estimé", f"{score_fatigue}/10")
with col_fat3:
    st.metric("😴 Récupération recommandée", f"{recup_finale}h",
              help="Avant de retravail le même groupe musculaire à intensité similaire")

# Jauge de fatigue visuelle
pct_fatigue = min(100, int(score_fatigue * 10))
if score_fatigue <= 4:
    couleur_fatigue = "#21c354"
    label_fatigue = "Fatigue modérée — récupération normale"
elif score_fatigue <= 7:
    couleur_fatigue = "#ff8800"
    label_fatigue = "Fatigue élevée — récupération active recommandée"
else:
    couleur_fatigue = "#ff4b4b"
    label_fatigue = "Fatigue très élevée — repos complet indispensable"

st.markdown(f"""
<div style="background:#f0f0f0; border-radius:8px; overflow:hidden; height:18px; margin:8px 0;">
  <div style="background:{couleur_fatigue}; width:{pct_fatigue}%; height:100%; border-radius:8px;
              transition:width 0.3s;"></div>
</div>
<p style="color:{couleur_fatigue}; font-weight:600; margin:0;">{label_fatigue}</p>
""", unsafe_allow_html=True)

# Conseils de récupération
with st.expander("Protocoles de récupération recommandés"):
    st.markdown(f"""
#### Récupération pour **{groupe_musculaire}** — {recup_finale}h estimées

| Méthode | Moment | Durée | Bénéfice |
|---|---|---|---|
| Cryothérapie locale | Dans les 2h post-séance | 10–15 min | Réduit l'inflammation aiguë |
| Cardio léger (marche) | J+1 | 20–30 min | Active la circulation sanguine |
| Stretching statique | J+1 ou J+2 | 15–20 min | Améliore l'amplitude articulaire |
| Fenêtre protéique | Dans les 2h post-séance | — | 0,3–0,4g de protéines/kg |
| Sommeil | Chaque nuit | 7–9h | Principal vecteur de synthèse protéique |
| Travail antagoniste léger | J+1 | — | Favorise la récupération active |

**Pour votre séance actuelle ({pct_actuel}% du 1RM, {nb_series} séries) :**
- Ingestion protéique recommandée : **{round(0.35 * 80, 0):.0f}–{round(0.4 * 80, 0):.0f}g** (base 80 kg)
- Hydratation : **+500 ml** par rapport à votre consommation habituelle
- Éviter : alcool, jeûne prolongé, cardio intense dans les {min(recup_finale, 12)}h
""")

# =============================================================================
# SECTION PLANIFICATION PROGRESSION SUR 4 SEMAINES
# =============================================================================
st.divider()
st.subheader("Planification de Progression — 4 Semaines")

st.markdown("""
Modèle de progression basé sur le principe de surcharge progressive.
Choisissez votre objectif principal pour générer un plan de 4 semaines.
""")

col_prog1, col_prog2 = st.columns(2)
with col_prog1:
    objectif_prog = st.selectbox(
        "Objectif principal",
        ["Force Max (1–3 reps)", "Force (4–6 reps)", "Hypertrophie (8–12 reps)", "Endurance-Force (15–20 reps)"]
    )
with col_prog2:
    increment_kg = st.number_input(
        "Incrément de charge par semaine (kg)",
        min_value=0.5, max_value=10.0, value=2.5, step=0.5,
        help="Progression réaliste : 1–2.5 kg/semaine pour la plupart des exercices"
    )

# Paramètres par objectif
prog_params = {
    "Force Max (1–3 reps)": {
        "semaines": [
            {"label": "S1 — Accumulation",    "pct": 85, "series": 5, "reps": "3",   "repos": "3–4 min", "rir": 3},
            {"label": "S2 — Intensification", "pct": 88, "series": 5, "reps": "2–3", "repos": "4 min",   "rir": 2},
            {"label": "S3 — Réalisation",      "pct": 92, "series": 4, "reps": "2",   "repos": "4–5 min", "rir": 1},
            {"label": "S4 — Deload (décharge)","pct": 70, "series": 3, "reps": "3",   "repos": "2 min",   "rir": 5},
        ]
    },
    "Force (4–6 reps)": {
        "semaines": [
            {"label": "S1 — Accumulation",    "pct": 80, "series": 4, "reps": "5",   "repos": "2–3 min", "rir": 4},
            {"label": "S2 — Intensification", "pct": 83, "series": 4, "reps": "4–5", "repos": "3 min",   "rir": 3},
            {"label": "S3 — Réalisation",      "pct": 87, "series": 4, "reps": "4",   "repos": "3–4 min", "rir": 2},
            {"label": "S4 — Deload (décharge)","pct": 65, "series": 3, "reps": "5",   "repos": "90 sec",  "rir": 6},
        ]
    },
    "Hypertrophie (8–12 reps)": {
        "semaines": [
            {"label": "S1 — Accumulation",    "pct": 70, "series": 3, "reps": "12",  "repos": "90 sec",  "rir": 4},
            {"label": "S2 — Intensification", "pct": 73, "series": 4, "reps": "10",  "repos": "2 min",   "rir": 3},
            {"label": "S3 — Surcharge",        "pct": 77, "series": 4, "reps": "8–9", "repos": "2 min",   "rir": 2},
            {"label": "S4 — Deload (décharge)","pct": 60, "series": 3, "reps": "12",  "repos": "60 sec",  "rir": 6},
        ]
    },
    "Endurance-Force (15–20 reps)": {
        "semaines": [
            {"label": "S1 — Accumulation",    "pct": 55, "series": 3, "reps": "20",  "repos": "60 sec",  "rir": 6},
            {"label": "S2 — Intensification", "pct": 58, "series": 3, "reps": "18",  "repos": "60 sec",  "rir": 5},
            {"label": "S3 — Surcharge",        "pct": 62, "series": 4, "reps": "15",  "repos": "90 sec",  "rir": 4},
            {"label": "S4 — Deload (décharge)","pct": 45, "series": 2, "reps": "20",  "repos": "45 sec",  "rir": 8},
        ]
    },
}

semaines_plan = prog_params[objectif_prog]["semaines"]
progression_rows = []
for i, sem in enumerate(semaines_plan):
    charge_sem = round(rm_final * sem["pct"] / 100 + i * increment_kg, 1)
    rir_s, rpe_s, _ = get_rir_info(sem["pct"])
    progression_rows.append({
        "Semaine": sem["label"],
        "% 1RM": f"{sem['pct']}%",
        "Charge (kg)": f"{charge_sem} kg",
        "Séries": sem["series"],
        "Reps": sem["reps"],
        "RIR cible": f"~{sem['rir']}",
        "RPE cible": f"{10 - sem['rir']}/10",
        "Repos": sem["repos"],
    })

df_prog = pd.DataFrame(progression_rows)
st.dataframe(df_prog, use_container_width=True, hide_index=True)

st.markdown("""
> **Principe de décharge (Deload, S4)** : réduire le volume et l'intensité de 30–40% permet
> au système nerveux central et aux tissus conjonctifs de se régénérer pleinement,
> favorisant une super-compensation pour le cycle suivant.
""")

# =============================================================================
# SECTIONS ORIGINALES (TABLE DE BERGER + TABLEAU DE PROGRAMMATION + FORMULES)
# =============================================================================

st.divider()
st.subheader("Table de Berger (1961) — correspondance reps / % 1RM")

if pct_berger:
    st.info(
        f"Pour **{reps} répétitions**, vous travaillez à **{pct_berger}%** de votre 1RM "
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
