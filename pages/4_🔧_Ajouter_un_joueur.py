import Reglement as coeur
import streamlit as st

# =========================
# Gestion des joueurs
# =========================
st.set_page_config(
    page_title="Ajouter un joueur",
    page_icon="⚙️",
)


# Fonction appelée lorsque l'utilisateur clique sur "Ajouter"
def add_player_callback():
    name = st.session_state["new_player_name_input"].strip()
    rating = st.session_state["new_player_rating_input"]
    if name == "" or name in coeur.players.keys():
        st.session_state["add_player_error"] = True
        return
    coeur.add_player(name, rating)
    coeur.players = coeur.get_players()
    st.session_state["add_player_error"] = False
    # Vider le champ en réinitialisant directement session_state
    st.session_state["new_player_name_input"] = ""
    st.session_state["new_player_rating_input"] = 1200

# Initialisation des variables de session_state
if "new_player_name_input" not in st.session_state:
    st.session_state["new_player_name_input"] = ""
if "new_player_rating_input" not in st.session_state:
    st.session_state["new_player_rating_input"] = 1200
if "add_player_error" not in st.session_state:
    st.session_state["add_player_error"] = False

with st.form("add_player_form"):
    st.subheader("⚙️ Ajouter un joueur")
    st.text_input("Nom du joueur", key="new_player_name_input")
    st.number_input("Elo initial", min_value=500, max_value=3000, key="new_player_rating_input")
    add_btn = st.form_submit_button("Ajouter", on_click=add_player_callback)

    if st.session_state["add_player_error"]:
        st.error("Ce joueur existe déjà")




#Section supprimer un joueur
#if coeur.players:
    #delete_choice = st.selectbox("Supprimer un joueur", ["--"] + list(coeur.players.keys()))
    #if delete_choice != "--":
        #if st.button(f"Supprimer {delete_choice}"):
            #coeur.delete_player(delete_choice)
            #st.warning(f"Joueur {delete_choice} supprimé")
            #coeur.players = coeur.get_players()
            #st.rerun()
            
