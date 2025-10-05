import streamlit as st
import math
import pandas as pd
import numpy as np
import sqlite3
from datetime import datetime
import json
import matplotlib.pyplot as plt
from supabase import create_client
import pytz
import os
#from dotenv import load_dotenv
from collections import Counter, defaultdict

# =========================
# FONCTIONS ELO
# =========================
def expected_score(rating_i, rating_j):
    return 1 / (1 + 10 ** ((rating_j - rating_i) / 400))

def normalize_scores(n):
    return [(n - place) / (n - 1) for place in range(1, n + 1)]

def update_ratings_individual(players, standings, K=24):
    """Met à jour pour un FFA individuel"""
    n = len(standings)
    S = normalize_scores(n)
    scores = {standings[i]: S[i] for i in range(n)}

    new_ratings = {}
    deltas = {}
    for player in standings:
        rating = players[player]
        expectations = [
            expected_score(rating, players[opponent])
            for opponent in standings if opponent != player
        ]
        E = sum(expectations) / (n - 1)
        delta = K * (scores[player] - E)
        deltas[player] = delta
        new_ratings[player] = round(rating + delta, 0)
    return new_ratings, deltas

def update_ratings_teams(players, teams, standings, K=24):
    """
    teams: dict ex { "Team1": ["A","B"], "Team2": ["C","D"] }
    standings: ex ["Team1","Team2"]
    """
    # Rating moyen par équipe
    team_ratings = {
        team: sum(players[p] for p in members) / len(members)
        for team, members in teams.items()
    }

    n = len(standings)
    S = normalize_scores(n)
    scores = {standings[i]: S[i] for i in range(n)}

    new_ratings = players.copy()
    deltas = {p: 0 for p in players}

    for team in standings:
        rating = team_ratings[team]
        expectations = [
            expected_score(rating, team_ratings[opp])
            for opp in standings if opp != team
        ]
        E = sum(expectations) / (n - 1)
        delta_team = K * (scores[team] - E)

        # Répartir équitablement entre les joueurs de l'équipe
        for member in teams[team]:
            delta = delta_team / len(teams[team])
            deltas[member] = delta
            new_ratings[member] = round(players[member] + delta, 0)

    return new_ratings, deltas

# =========================
# BASE DE DONNÉES SUPABASE
# =========================
from supabase import create_client
from datetime import datetime
import json
import os
#from dotenv import load_dotenv

#SUPABASE_URL = 'https://tphqhevpmlsksmzidara.supabase.co'
#SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRwaHFoZXZwbWxza3NtemlkYXJhIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTk1NjcwNDksImV4cCI6MjA3NTE0MzA0OX0.zIMfyAHH7pUui0fReFOwTzhUpwHn5Fu49g-czNoxF38'
SUPABASE_URL = st.secrets["supabase"]["url"]
SUPABASE_KEY = st.secrets["supabase"]["key"]
supabase = create_client(SUPABASE_URL,SUPABASE_KEY)

def get_players():
    """Retourne un dict {nom: rating} depuis la table players."""
    response = supabase.table("players").select("*").order("id_player", desc=False).execute()
    data = response.data or []
    return {p["name"]: p["rating"] for p in data}

def get_max_elo_players():
    """Retourne un dict {nom: rating} depuis la table players."""
    response = supabase.table("players").select("*").execute()
    data = response.data or []
    max_ratings = {}
    for player in data:
        name = player.get("name")
        rating = player.get("rating")
        if name not in max_ratings or rating > max_ratings[name]:
            max_ratings[name] = rating
        
    return max_ratings

def save_players(players):
    """Met à jour les Elo des joueurs dans Supabase."""
    for name, rating in players.items():
        supabase.table("players").upsert({"name": name, "rating": rating}).execute()

def add_player(name, rating):
    """Ajoute un joueur s’il n’existe pas déjà."""
    existing = supabase.table("players").select("*").eq("name", name).execute()
    if existing.data:
        # Le joueur existe déjà, on met juste à jour son Elo
        supabase.table("players").update({"rating": rating}).eq("name", name).execute()
    else:
        supabase.table("players").insert({"name": name, "rating": rating}).execute()

def delete_player(name):
    """Supprime un joueur par son nom."""
    supabase.table("players").delete().eq("name", name).execute()

# =========================
# GESTION DES MATCHS
# =========================

def add_match(standings, players_after, participants):
    """
    Enregistre une partie dans Supabase.

    standings : liste ordonnée des équipes
    players_after : dict {joueur: Elo après la partie}
    participants : liste des joueurs ayant réellement joué
    """
    TIMEZONE = 'Europe/Paris'
    utc_now = datetime.now(pytz.utc)
    paris_tz = pytz.timezone(TIMEZONE)
    paris_now = utc_now.astimezone(paris_tz)
    localized_date_iso = paris_now.isoformat(timespec="seconds")
    snapshot = {p: players_after[p] for p in participants}

    supabase.table("matches").insert({
        "date": localized_date_iso,
        "standings": ",".join(standings),
        "ratings": json.dumps(snapshot)
    }).execute()

def get_matches():
    """Retourne la liste des matchs triés du plus récent au plus ancien."""
    response = supabase.table("matches").select("date, standings, ratings").order("date", desc=True).execute()
    data = response.data or []
    return [(m["date"], m["standings"], m["ratings"]) for m in data]

def get_history():
    """Retourne l’historique des parties dans l’ordre chronologique."""

    response = supabase.table("matches").select("date, ratings").order("date", desc=False).execute()

    data = response.data or []
    return [(m["date"], m["ratings"]) for m in data]


def nb_games_played_by_player():
    """
    """
    response = supabase.table("matches").select("date, ratings").order("date", desc=False).execute()
    data = response.data or []
    player_plays = []
    
    for player_record in data:
        list_player = json.loads(player_record["ratings"]).keys()
        for player in list_player:
            player_plays.append(player)
            
    return Counter(player_plays)

def nb_games_played_by_day():
    """
    """
    response = supabase.table("matches").select("date, ratings").order("date", desc=False).execute()
    data = response.data or []
    day_plays = []
    
    for date in data:
        day_plays.append(date["date"][:10])
    return Counter(day_plays)

def players_by_day():
    """
    Retourne un dictionnaire {date: [liste de joueurs distincts ayant joué ce jour-là]}.
    """
    response = supabase.table("matches").select("date, ratings").order("date", desc=False).execute()
    data = response.data or []
    
    # Dictionnaire : date -> set(joueurs)
    players_per_day = defaultdict(set)
    
    for match in data:
        date_str = match["date"][:10]  # format YYYY-MM-DD
        ratings_json = match.get("ratings", "{}")

        try:
            ratings = json.loads(ratings_json)
            for player in ratings.keys():
                players_per_day[date_str].add(player)
        except Exception:
            pass  # si un champ ratings est vide ou corrompu, on ignore

    # Conversion des sets en listes pour un affichage plus simple
    players_per_day = {d: sorted(list(players)) for d, players in players_per_day.items()}

    return players_per_day



players = get_players()
