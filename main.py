import os

from flask import Flask, render_template, request, redirect, session
import base64
import secrets
from hashlib import sha256
from forms import RegistrationForm
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import recommendation_project as rp
from builtins import zip

app = Flask(__name__)
app.secret_key = os.urandom(24)

REDIRECT_URI = 'https://9000-idx-recommendation-app-1719335238204.cluster-ux5mmlia3zhhask7riihruxydo.cloudworkstations.dev/callback'
SCOPE = ['''user-library-read user-read-private
         user-read-email user-read-currently-playing''']


def refresh_token(sp_oauth):
    '''Refreshes user access token.'''
    new_token = sp_oauth.refresh_access_token(sp_oauth.get_cached_token()['refresh_token'])
    return new_token['access_token']


@app.route("/")
def index():
    return render_template('index.html')


@app.route("/login", methods=['GET', 'POST'])
def login():
    form = RegistrationForm()
    if 'access_token' in session:
        return redirect('/recommendations')

    if form.validate_on_submit():
        # Store form data in session for later use
        session['client_id'] = form.client_id.data
        session['client_secret'] = form.client_secret.data

        # Generate code verifier and challenge
        #code_verifier = secrets.token_urlsafe(128)
        #code_challenge = base64.urlsafe_b64encode(
        #    sha256(code_verifier.encode('utf-8')).digest()
        #).decode('utf-8').rstrip('=')

        # Store code verifier in session
        #session['code_verifier'] = code_verifier

        # Update SpotifyOAuth object with user-provided data
        sp_oauth = SpotifyOAuth(client_id=session['client_id'], 
                                client_secret=session['client_secret'], 
                                redirect_uri=REDIRECT_URI, 
                                scope=SCOPE)
        
        #sp_oauth.code_challenge = code_challenge

        authorize_url = sp_oauth.get_authorize_url()
        return redirect(authorize_url)
    
    print("Authentication failed.")
    return render_template('login.html', form=form)


@app.route("/callback")
def callback():
    code = request.args.get('code')
    #code_verifier = session.get('code_verifier')

    sp_oauth = SpotifyOAuth(client_id=session['client_id'], 
                                client_secret=session['client_secret'], 
                                redirect_uri=REDIRECT_URI, 
                                scope=SCOPE)

    token_info = sp_oauth.get_access_token(code)
    session['access_token'] = token_info['access_token']
    return redirect('/recommendations')

@app.route("/recommendations")
def recommendations():
    if 'access_token' not in session:
        return redirect('/login')

    sp = spotipy.Spotify(auth=session['access_token'])

    return render_template('recommendations.html')

@app.route("/results")
def results():
    if 'access_token' not in session:
        return redirect('/login')
    
    sp = spotipy.Spotify(auth=session['access_token'])

    choice = request.args.get('choice')

    if choice == 'top_songs':
        songs_short_term = rp.get_top_tracks('short_term', sp)
        songs_medium_term = rp.get_top_tracks('medium_term', sp)
        songs_long_term = rp.get_top_tracks('long_term', sp)

        data = [{'title': 'Top Songs (Past Month)', 'table': songs_short_term}, 
                {'title': 'Top Songs (Past 6 Months)', 'table': songs_medium_term}, 
                {'title': 'Top Songs (All Time)', 'table': songs_long_term}]
            
        columns = [' ', 'Song Title', 'Artist(s)']

        return render_template('results.html', title='Top Songs', data=data, columns=columns)
    
    elif choice == 'top_artists':
        artists_short_term = rp.get_top_artists('short_term', sp)
        artists_medium_term = rp.get_top_artists('medium_term', sp)
        artists_long_term = rp.get_top_artists('long_term', sp)

        data = [{'title': 'Top Artists (Past Month)', 'table': artists_short_term}, 
                {'title': 'Top Artists (Past 6 Months)', 'table': artists_medium_term}, 
                {'title': 'Top Artists (All Time)', 'table': artists_long_term}]
            
        columns = [' ', 'Artist', 'Popularity', 'Genres']

        return render_template('results.html', data=data, columns=columns)
    
    #elif choice == 'recent_songs':
    #    recent_songs = rp.get_recent_tracks(sp)
    #
    #    data = {'title': 'Recent Songs', 'table': recent_songs}
    #    columns = ['', 'Song Title', 'Artist(s)']

    #    return render_template('results.html', data=data, columns=columns)
    
    elif choice == 'recent_artists':
        recent_artists = rp.get_recent_artists(sp)

        data = {'title': 'Recent Artists', 'table': recent_artists}
        columns = [' ', 'Artist', 'Popularity', 'Genres']

        return render_template('results.html', data=data, columns=columns)
    
    elif choice == 'recommend_me':
        recommendations = rp.get_recommendations(sp)

        return render_template('results.html', data=recommendations)

    else:
        return "invalid choice", 400


@app.route("/about")
def about():
    return render_template('about.html')

@app.route("/logout")
def logout():
    if 'access_token' in session:
        session.clear()
        return redirect('/')
    else:
        return redirect('/login')

def main():
    app.run(port=int(os.environ.get('PORT', 80)))

if __name__ == "__main__":
    main()
