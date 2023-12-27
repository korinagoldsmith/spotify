import streamlit as st
import spotipy 
from spotipy.oauth2 import SpotifyOAuth
import webbrowser
import os

if "cached_token" not in st.session_state:
    st.session_state["cached_token"] = ""
st.session_state["signed_in"] = False
st.session_state["code"] = ""

sp_oauth = SpotifyOAuth(client_id=st.secrets["client_id"],
                        client_secret=st.secrets["client_secret"],
                        redirect_uri=st.secrets["redirect_uri"],
                        scope="user-library-read user-top-read")

def get_token(oauth, code):

    token = oauth.get_access_token(code, as_dict=False, check_cache=False)
    # remove cached token saved in directory
    os.remove(".cache")
    
    # return the token
    return token



def sign_in(token):
    sp = spotipy.Spotify(auth=token)
    return sp

def app_sign_in():
    try:
        sp = sign_in(st.session_state["cached_token"])
    except Exception as e:
        app_display_welcome()
        st.error("An error occurred during sign-in!")
        st.write("The error is as follows:")
        st.write(e)
    else:
        st.session_state["signed_in"] = True
        #st.success("Sign in success!")
        
    return sp

def app_get_token():
    try:
        token = get_token(sp_oauth, st.session_state["code"])
    except Exception as e:
        app_display_welcome()
        st.error("An error occurred during token retrieval!")
        st.write("The error is as follows:")
        st.write(e)
    else:
        st.session_state["cached_token"] = token

def app_display_welcome():
    if st.button("Sign in with Spotify"):
        auth_url = sp_oauth.get_authorize_url()
        webbrowser.open(auth_url)
        st.markdown(f"Click the following link to sign in: [{auth_url}]({auth_url})")

sp = spotipy.Spotify(auth_manager=sp_oauth)

def display(menu, amount, time, duration):
    st.title(f"{amount} {menu.lower()} on Spotify {duration}")
    columns = st.columns(2)
    counter = 0
    if menu == "Artists":
        if amount == "Top 10":
            limit = 10
        if amount == "Top 20":
            limit = 20
        if amount == "Top 50":
            limit = 50
        top_artists = sp.current_user_top_artists(limit=limit, time_range=time)
        for artist in top_artists['items']:
            with columns[counter % 2]:
                st.subheader(f"{counter + 1}. [{artist['name']}]({artist['external_urls']['spotify']})")
                st.markdown(f'<a href="{artist["external_urls"]["spotify"]}"><img src="{artist["images"][0]["url"]}" width="250"></a>', unsafe_allow_html=True)

            counter += 1
            #st.json(artist)

    if menu == "Tracks":
        if amount == "Top 10":
            limit = 10
        if amount == "Top 20":
            limit = 20
        if amount == "Top 50":
            limit = 50
        top_tracks = sp.current_user_top_tracks(limit=limit, time_range=time)
        for track in top_tracks['items']:
            with columns[counter % 2]:
                st.write(f"**{counter + 1}. [{track['name']} by {track['artists'][0]['name']}]({track['external_urls']['spotify']})** ")
                album_id = track['album']['id']
                album_details = sp.album(album_id)
                st.markdown(f'<a href="{album_details["external_urls"]["spotify"]}"><img src="{album_details["images"][0]["url"]}" width="{250}"></a>', unsafe_allow_html=True)

            counter += 1

#navigation bar
st.sidebar.title("Menu")
menu_choice = st.sidebar.radio("",["Artists", "Tracks"]) #NEW 3
amount_choice = st.sidebar.radio("",["Top 10", "Top 20", "Top 50"])
time_choice = st.sidebar.radio("", ["Last month", "6 months", "All time"])
st.sidebar.image("spotify_logo.png", width = 200)

url_params = st.experimental_get_query_params()
# attempt sign in with cached token
if st.session_state["cached_token"] != "":
    sp = app_sign_in()
    if time_choice == "Last month":
        display(menu_choice, amount_choice, "short_term", "last month")
    if time_choice == "6 months":
        display(menu_choice, amount_choice, "medium_term", "in the last 6 months")
    if time_choice == "All time":
        display(menu_choice, amount_choice, "long_term", "of all time")
# if no token, but code in url, get code, parse token, and sign in
elif "code" in url_params:
    # all params stored as lists, see doc for explanation
    st.session_state["code"] = url_params["code"][0]
    app_get_token()
    sp = app_sign_in()
    if time_choice == "Last month":
        display(menu_choice, amount_choice, "short_term", "last month")
    if time_choice == "6 months":
        display(menu_choice, amount_choice, "medium_term", "in the last 6 months")
    if time_choice == "All time":
        display(menu_choice, amount_choice, "long_term", "of all time")
# otherwise, prompt for redirect
else:
    app_display_welcome()