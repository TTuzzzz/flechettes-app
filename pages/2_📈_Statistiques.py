import Reglement as coeur
import streamlit as st
import pandas as pd
import json
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import numpy as np
from datetime import datetime
import datetime as dt

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


# =========================
# Calcul du dernier delta Elo (approche chronologique)
# =========================
matches = coeur.get_matches()
players = coeur.get_players()
last_deltas = {}


if matches:
    # Récupérer tous les ratings historiques sous forme chronologique
    evolution = coeur.get_players_ratings_history()
    # Identifier les joueurs du dernier match
    matches_sorted = sorted(matches, key=lambda m: m[0])
    last_match = matches_sorted[-1]
    last_ratings = json.loads(last_match[2])
    participants = list(last_ratings.keys())

    # Calcul du delta pour les participants uniquement
    for player in participants:
        if player in evolution and len(evolution[player]) >= 2:
            last_deltas[player] = int(round(evolution[player][0] - evolution[player][1]))
        else:
            last_deltas[player] = 0  # cas d’un joueur qui joue pour la première fois

# =========================
# Construction du tableau classement
# =========================
def delta_icon(delta):
    if delta > 0:
        return f"💹 {delta}"
    elif delta < 0:
        return f"📉 {delta}"
    else:
        return "⚪ 0"

# Créer le DataFrame principal
df = pd.DataFrame([
    {
        "Joueur": name,
        "Elo": rating,
        "Dernière variation": delta_icon(last_deltas.get(name, 0))
    }
    for name, rating in players.items()
]).sort_values(by="Elo", ascending=False)

df['Joueur'] = df['Joueur'].replace("Pauline B", "Pauline B 💪")
df['Rang'] = df['Elo'].rank(method='min', ascending=False)
df['Elo'] = pd.to_numeric(df['Elo'], downcast='integer', errors='coerce')
df['Elo'] = df['Elo'].apply(lambda x: f"{x:,.0f}".replace(",", " "))
df['Rang'] = pd.to_numeric(df['Rang'], downcast='integer', errors='coerce')

with st.container(border=True):
    # ===============================
    # Sélection d’une date à afficher
    # ===============================
    st.header("Résumé quotidien ⌚")
    matches = coeur.get_matches()
    if not matches:
        st.info("Aucune partie enregistrée pour le moment.")
    else:
        # Liste de toutes les dates présentes dans la table matches
        dates_disponibles = sorted({m[0][:10] for m in matches})
        default_index = len(dates_disponibles) - 1  # dernière date par défaut
        selected_date = st.date_input(
            "📅 Choisis une date",
            value=dt.date.fromisoformat(dates_disponibles[default_index]),
            min_value=dt.date.fromisoformat(dates_disponibles[0]),
            max_value=dt.date.fromisoformat(dates_disponibles[-1])
        )
        selected_str = str(selected_date)

        # ==========================
        # Infos générales du jour
        # ==========================
        ppd = coeur.nb_games_played_by_day()
        nb_parties = ppd.get(selected_str, 0)

        # Joueurs ayant joué ce jour-là
        players_per_day = coeur.players_by_day()
        players_day = players_per_day.get(selected_str, [])

        if players_day:
            if len(players_day) == 2:
                joueurs_str = f"**{players_day[0]}** et **{players_day[1]}** ont joué ce jour-là."
            elif len(players_day) > 2:
                joueurs_str = ", ".join(players_day[:-1]) + f" et {players_day[-1]}"
                joueurs_str = f"**{joueurs_str}** ont joué ce jour-là."
            else:
                joueurs_str = f"**{players_day[0]}** a joué ce jour-là."
        else:
            joueurs_str = "😴 Aucun joueur n’a disputé de partie ce jour-là."

        # ==========================
        # Affichage des infos
        # ==========================
        st.markdown(f"📊 **{nb_parties}** partie(s) disputée(s) le **{selected_str}**.")
        st.markdown(joueurs_str)

        # ==========================
        # Tableau des matchs du jour
        # ==========================
        day_matches = [m for m in matches if m[0].startswith(selected_str)]

        if day_matches:
            data = []
            for date, standings_raw, ratings_json in day_matches:
                try:
                    standings = standings_raw.split(",") if isinstance(standings_raw, str) else standings_raw
                    standings_clean = []
                    for i, team in enumerate(standings, start=1):
                        # Nettoyage pour afficher j1 et j2 au lieu du nom d'équipe
                        team_players = team.replace("[", "").replace("]", "").replace("'", "").split("&")
                        team_players = [p.strip() for p in team_players if p.strip()]
                        if len(team_players) == 1:
                            team_str = team_players[0]
                        else:
                            team_str = " et ".join(team_players)
                        standings_clean.append(f"{i}ᵉ : {team_str}")
                    data.append({
                        "Heure": date[11:19],
                        "Classement": "\n".join(standings_clean)
                    })
                except Exception:
                    continue

            df_matches = pd.DataFrame(data)
            st.subheader("🗒️ Matchs disputés ce jour-là")
            st.dataframe(df_matches, use_container_width=True)
        else:
            st.info("Aucun match enregistré pour cette date.")

with st.container(border=True):
    st.header("Evaluation actuelle 🎯")
    st.dataframe(df.set_index("Rang"))


    ########################
    ##Section Graphique#####
    ########################

    
    #st.subheader("📈 Évolution Elo des joueurs")
        
    #history = coeur.get_history()
    #players = coeur.get_players()

    #if players:
        #all_players = list(players.keys())
        # Elo initial en partie 0
        #ratings_by_player = {p: [1200] for p in all_players}

        # Charger historique
        #for i, (date, ratings_json) in enumerate(history, start=1):
            #ratings = json.loads(ratings_json)
            #for p in all_players:
                #if p in ratings:
                    #ratings_by_player[p].append(ratings[p])
                #else:
                    # Répéter le dernier score si joueur absent
                    #ratings_by_player[p].append(ratings_by_player[p][-1])

        # Axe des X : parties
        #timeline = list(range(len(history) + 1))

        # Création du graphique Plotly
        #fig = go.Figure()

        #for p, values in ratings_by_player.items():
            #fig.add_trace(go.Scatter(
                #x=timeline,
                #y=values,
                #mode='lines+markers',
                #name=p,
                #text=[f"{p}: {int(v):,}".replace(","," ") for v in values],  # info-bulle : séparateur de millier et pas de décimale
                #hoverinfo="text",
                #line=dict(width=2)
            #))

        # Mise en page
        #fig.update_layout(
            #title="Évolution Elo des joueurs",
            #xaxis=dict(title="Nombre de parties", dtick=1),
            #yaxis=dict(title="Elo"),
            #legend=dict(
                #orientation="h",  # horizontale
                #yanchor="bottom",
                #y=-0.3,           # en dessous du graphique
                #xanchor="center",
                #x=0.5
            #),
            #margin=dict(t=50, b=80),  # marge pour légende
            #hovermode="x unified",
            #template="plotly_white"
        #)


        #st.plotly_chart(fig, use_container_width=True)

    #else:
    #    st.info("Aucun joueur enregistré.")


#################
###STATS INDIV###
#################
with st.container(border=True):
    st.subheader("Statistiques individuelles")

    max_rating = coeur.get_max_elo_players()
    nb_matchs = coeur.nb_games_played_by_player()
    players_list = list(coeur.get_players().keys())
    selected_player = st.selectbox("Filtre sur un joueur :"
                                    , players_list
                                    ,index=None
                                    ,placeholder="Choisir le joueur",)
    if selected_player:
        st.write("Indicateurs clés de " + selected_player)
        a, b = st.columns(2)
        a.metric("ELO Maximum :", max_rating[selected_player])
        b.metric("Nombre de parties jouées :", nb_matchs[selected_player])

     
