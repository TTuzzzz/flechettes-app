import Reglement as coeur
import streamlit as st
import pandas as pd
import json
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import numpy as np
from datetime import datetime

st.set_page_config(
    page_title="Statistique",
    page_icon="📈",
)

# Init DB
#coeur.init_db()

# Charger joueurs
players = coeur.get_players()
if not players:
    players = {"Tom": 1200, "Vincent": 1200, "Xavier": 1200, "Pauline B": 1200, "Pauline F": 1200}
    coeur.save_players(players)


# Récupérer le dernier match
matches = coeur.get_matches()
last_deltas = {}

def parse_date_safe(s):
    if s is None:
        return datetime.min
    if isinstance(s, datetime):
        return s
    for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
        try:
            return datetime.fromisoformat(s) if "T" in s else datetime.strptime(s, fmt)
        except Exception:
            pass
    try:
        return datetime.fromisoformat(str(s))
    except Exception:
        return datetime.min

def parse_ratings_field(field):
    if field is None:
        return {}
    if isinstance(field, dict):
        return {str(k): float(v) for k, v in field.items()}
    if isinstance(field, str):
        try:
            parsed = json.loads(field)
            if isinstance(parsed, dict):
                return {str(k): float(v) for k, v in parsed.items()}
        except Exception:
            try:
                parsed = eval(field)
                if isinstance(parsed, dict):
                    return {str(k): float(v) for k, v in parsed.items()}
            except Exception:
                pass
    return {}

matches = coeur.get_matches()
last_deltas = {}

if matches:
    # tri des matches par date décroissante
    matches_sorted = sorted(
        matches,
        key=lambda m: parse_date_safe(m[0]),
        reverse=True
    )

    last_match = matches_sorted[0]
    last_ratings = parse_ratings_field(last_match[2])

    if len(matches_sorted) > 1:
        prev_match = matches_sorted[1]
        prev_ratings = parse_ratings_field(prev_match[2])
    else:
        prev_ratings = {}

    for player, rating_after in last_ratings.items():
        rating_before = prev_ratings.get(player)
        if rating_before is None:
            # remonter la pile pour trouver le dernier rating connu
            for m in matches_sorted[1:]:
                r = parse_ratings_field(m[2])
                if player in r:
                    rating_before = r[player]
                    break
        if rating_before is None:
            rating_before = coeur.players.get(player, 1200)

        last_deltas[player] = int(round(float(rating_after) - float(rating_before)))



# Fonction pour transformer le delta en flèche/pictogramme
def delta_icon(delta):
    if delta > 0:
        return f"💹 {delta}"
    elif delta < 0:
        return f"📉 {delta}"
    else:
        return "⚪ 0"

# Créer le DataFrame
df = pd.DataFrame([
    {
        "Joueur": name,
        "Elo": rating,
        "Dernière variation": delta_icon(last_deltas.get(name, 0))
    }
    for name, rating in coeur.players.items()
]).sort_values(by="Elo", ascending=False)

df['Rang'] = df['Elo'].rank(method='min', ascending=False)


df['Elo'] = pd.to_numeric(df['Elo'], downcast='integer', errors='coerce')
df['Elo'] = df['Elo'].apply(lambda x: f"{x:,.0f}".replace(",", " "))
df['Rang'] = pd.to_numeric(df['Rang'], downcast='integer', errors='coerce')

st.header("Evaluation actuelle 🎯")
st.dataframe(df.set_index("Rang"))

########################
##Section Graphique#####
########################


st.subheader("📈 Évolution Elo des joueurs")
    
history = coeur.get_history()
players = coeur.get_players()

if players:
    all_players = list(players.keys())
    # Elo initial en partie 0
    ratings_by_player = {p: [1200] for p in all_players}

    # Charger historique
    for i, (date, ratings_json) in enumerate(history, start=1):
        ratings = json.loads(ratings_json)
        for p in all_players:
            if p in ratings:
                ratings_by_player[p].append(ratings[p])
            else:
                # Répéter le dernier score si joueur absent
                ratings_by_player[p].append(ratings_by_player[p][-1])

    # Axe des X : parties
    timeline = list(range(len(history) + 1))

    # Création du graphique Plotly
    fig = go.Figure()

    for p, values in ratings_by_player.items():
        fig.add_trace(go.Scatter(
            x=timeline,
            y=values,
            mode='lines+markers',
            name=p,
            text=[f"{p}: {int(v):,}".replace(","," ") for v in values],  # info-bulle : séparateur de millier et pas de décimale
            hoverinfo="text",
            line=dict(width=2)
        ))

    # Mise en page
    fig.update_layout(
        title="Évolution Elo des joueurs",
        xaxis=dict(title="Nombre de parties", dtick=1),
        yaxis=dict(title="Elo"),
        legend=dict(
            orientation="h",  # horizontale
            yanchor="bottom",
            y=-0.3,           # en dessous du graphique
            xanchor="center",
            x=0.5
        ),
        margin=dict(t=50, b=80),  # marge pour légende
        hovermode="x unified",
        template="plotly_white"
    )


    st.plotly_chart(fig, use_container_width=True)

else:
    st.info("Aucun joueur enregistré.")
    

#################
###STATS INDIV###
#################
st.subheader("Statistiques individuelles")

max_rating = coeur.get_max_elo_players()
nb_matchs = coeur.nb_games_played_by_player()
players_list = list(coeur.players.keys())
selected_player = st.selectbox("Filtre sur un joueur :"
                                , players_list
                                ,index=None
                                ,placeholder="Choisir le joueur",)
if selected_player:
    st.write("Indicateurs clés de " + selected_player)
    a, b = st.columns(2)
    a.metric("ELO Maximum :", max_rating[selected_player])
    b.metric("Nombre de parties jouées :", nb_matchs[selected_player])
     