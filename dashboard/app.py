import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Configuration de la page
st.set_page_config(
    page_title="Getaround - Dashboard Produit",
    page_icon="🚗",
    layout="wide"
)

# 2. En-tête du Dashboard
st.title("🚗 Getaround : Simulateur de Retards & Tarification")
st.markdown("Ce tableau de bord permet à l'équipe Produit de simuler l'impact d'un délai minimum entre deux locations.")

# 3. Chargement et mise en cache des données (Optimisation)
@st.cache_data
def load_data():
    # Chemin relatif depuis la racine du projet vers le dossier data
    return pd.read_excel("data/get_around_delay_analysis (1).xlsx")

df = load_data()

# 4. Nettoyage basique en direct
# On supprime les lignes où il manque le temps entre deux locations pour faire des calculs propres
df_clean = df.dropna(subset=['time_delta_with_previous_rental_in_minutes'])

# 5. Section 1 : Analyse Graphique
st.subheader("📊 1. Distribution des retards au Checkout")
# Création du graphique interactif avec Plotly
fig = px.histogram(
    df, 
    x="delay_at_checkout_in_minutes", 
    nbins=100,
    title="Analyse des minutes de retard (Négatif = En avance)",
    color_discrete_sequence=['#FF4B4B']
)
st.plotly_chart(fig, use_container_width=True)

# 6. Section 2 : Le Simulateur Métier
st.subheader("⚙️ 2. Simulateur de Seuil de Battement (Threshold)")
st.markdown("Testez différents délais pour voir combien de locations seraient impactées.")

# Création des filtres interactifs
col_filtre1, col_filtre2 = st.columns(2)
with col_filtre1:
    threshold = st.slider("Délai minimum imposé (en minutes) :", min_value=0, max_value=120, value=30, step=15)
with col_filtre2:
    scope = st.selectbox("Application de la règle (Scope) :", ["Toutes les voitures", "Uniquement Connect"])

# 7. Application des règles métier selon les choix de l'utilisateur
if scope == "Uniquement Connect":
    df_simul = df_clean[df_clean['checkin_type'] == 'connect']
else:
    df_simul = df_clean.copy()

# 8. Calculs d'impact
total_rentals = len(df_simul)
impacted_rentals = len(df_simul[
    (df_simul['time_delta_with_previous_rental_in_minutes'] < threshold) & 
    (df_simul['time_delta_with_previous_rental_in_minutes'] > 0)
])
revenus_perdus_pourcentage = (impacted_rentals / total_rentals) * 100 if total_rentals > 0 else 0

# 9. Affichage des KPIs (Indicateurs Clés de Performance)
st.markdown("### 📈 Résultats de la simulation")
kpi1, kpi2, kpi3 = st.columns(3)
kpi1.metric(label="Total locations analysées", value=total_rentals)
kpi2.metric(label="Locations annulées (Impactées)", value=impacted_rentals)
kpi3.metric(label="Perte de revenus estimée", value=f"{revenus_perdus_pourcentage:.1f} %")