import Reglement as coeur
import streamlit as st

st.set_page_config(
    page_title="Ajouter une partie",
    page_icon="⚙️",
    layout="wide"
)

# =========================
# Nouvelle partie (mode unique)
# =========================
with st.container(border=True):
    st.subheader("Ajouter une partie 🎯")

    players_list = list(coeur.get_players().keys())
    selected_players = st.multiselect("Sélectionne les joueurs qui participent :", sorted(players_list),placeholder="Joueurs")

    if len(selected_players) >= 2:
        st.markdown("### ⚙️ Configuration des équipes")

        teams = {}
        used_players = set()

        # On laisse l'utilisateur définir autant d'équipes qu'il veut
        for i in range(len(selected_players)):
            available = [p for p in selected_players if p not in used_players]
            if not available:
                break
            team_members = st.multiselect(f"Équipe {i+1}", available, key=f"team_{i}")
            if not team_members:
                continue

            # Nom spécial si l'équipe est exactement ["Tom", "Marouane"]
            if sorted(team_members) == sorted(["Tom", "Marouane"]):
                team_name = "Meilleur Duo"
            else:
                team_name = " et ".join(sorted(team_members))

            teams[team_name] = team_members
            used_players.update(team_members)

        if len(teams) >= 2:
            standings = st.multiselect("Classement final des équipes (ordre de victoire)", list(teams.keys()))
            if len(standings) == len(teams):
                if st.button("Enregistrer la partie"):
                    new_ratings, deltas = coeur.update_ratings_teams(coeur.players, teams, standings, K=24)
                    updated_players = coeur.players.copy()
                    updated_players.update(new_ratings)
                    coeur.save_players(updated_players)

                    # 🔹 Nouveau : récupérer tous les joueurs ayant participé
                    participants = []
                    for members in teams.values():
                        participants.extend(members)

                    coeur.add_match(standings, updated_players, participants)  # <-- nouvelle signature

                    st.success("Classement mis à jour ✅")
                    st.json({p: round(d, 0) for p, d in deltas.items()})
                    coeur.history = coeur.get_history()
                    coeur.players = coeur.get_players()
                    st.rerun()  # correction : use experimental_rerun()
                    
        else:
            st.info("⚠️ Crée au moins 2 équipes pour enregistrer une partie.")

