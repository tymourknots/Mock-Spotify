import os
  # accessible as a variable in index.html:
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response, abort, session, url_for, jsonify, send_from_directory
from flask_cors import CORS
from flask_session import Session


tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, static_folder='static')
app.secret_key = os.urandom(24)
CORS(app, supports_credentials=True, resources={r"/*": {"origins": "http://localhost:3000"}})

app.config['SESSION_TYPE'] = 'filesystem'
Session(app)


DATABASEURI = "postgresql://postgres:trymour@localhost:5432/postgres"



engine = create_engine(DATABASEURI)

conn = engine.connect()


conn.execute(text("""CREATE TABLE IF NOT EXISTS test (
  id serial,
  name text
);"""))
conn.execute(text("""INSERT INTO test(name) VALUES ('grace hopper'), ('alan turing'), ('ada lovelace');"""))

# To make the queries run, we need to add this commit line

conn.commit() 

@app.before_request
def before_request():
  """
  This function is run at the beginning of every web request
  (every time you enter an address in the web browser).
  We use it to setup a database connection that can be used throughout the request.

  The variable g is globally accessible.
  """
  try:
    g.conn = engine.connect()
  except:
    print("uh oh, problem connecting to database")
    import traceback; traceback.print_exc()
    g.conn = None

@app.teardown_request
def teardown_request(exception):
  """
  At the end of the web request, this makes sure to close the database connection.
  If you don't, the database could run out of memory!
  """
  try:
    g.conn.close()
  except Exception as e:
    pass


@app.route('/')
@app.route('/<path:path>')
def serve_react(path=None):
    """
    Serve the React app from the build folder.
    """
    if path is None or path == '':
        path = 'index.html'
    return send_from_directory('../mock-spotify/build', path)

@app.route('/api/session', methods=['GET'])
def get_session():
    username = session.get('username')
    print(f"Session username: {username}")  # Debugging log
    return jsonify({"username": username}) if username else jsonify({"username": None})





# Example of adding new data to the database
@app.route('/add', methods=['POST'])
def add(): 
  name = request.form['name']
  params_dict = {"name":name}
  g.conn.execute(text('INSERT INTO test(name) VALUES (:name)'), params_dict)
  g.conn.commit()
  return redirect('/')

# Route for searching a song and also displaying the song's page
@app.route('/api/search_song', methods=['GET'])
def search_song():
    song_title = request.args.get('song_title', '').strip()
    song_id = request.args.get('song_id', '').strip()

    if not song_id and not song_title:
        # Return an error if both parameters are missing
        return jsonify({"songs": [], "playlists": [], "error": "No song ID or title provided"}), 400

    result = []
    playlists = []

    # Only execute the query if song_id or song_title is provided
    if song_id or song_title:
        query = text("""
            SELECT Song.*, Artist.Name AS ArtistName, Artist.ArtistID,
              albumBelong.Title AS AlbumTitle, albumBelong.AlbumID, albumBelong.Genre AS AlbumGenre
            FROM Song
            JOIN contains2 ON Song.songID = contains2.songID
            JOIN albumBelong ON contains2.AlbumID = albumBelong.AlbumID
            JOIN Artist ON albumBelong.ArtistID = Artist.ArtistID
            WHERE (:song_id IS NOT NULL AND Song.songID = :song_id)
               OR (:song_title IS NOT NULL AND Song.title ILIKE :song_title)
        """)
        result = g.conn.execute(query, {'song_id': song_id or None, 'song_title': f"%{song_title}%" if song_title else None}).fetchall()

        if result and not song_id:
            song_id = result[0][0]  # Extract the song ID from the first result if searching by title

        if song_id:
            playlist_query = text("""
                SELECT Playlist.* FROM Playlist
                JOIN contains1 ON Playlist.PlaylistID = contains1.PlaylistID
                WHERE contains1.songID = :song_id
            """)
            playlists = g.conn.execute(playlist_query, {'song_id': song_id}).fetchall()

    # Format response data
    songs = [{
        "id": song[0].strip(),
        "title": song[1],
        "album": {"id": song[10].strip(), "title": song[9]},
        "artist": {"id": song[8], "name": song[7]},
        "genre": song[-1],
        "duration": song[3],
        "releaseYear": song[4],
        "plays": song[6]
    } for song in result]

    playlists_data = [{"id": playlist[0].strip(), "title": playlist[1]} for playlist in playlists]

    return jsonify({"songs": songs, "playlists": playlists_data})





# Route for searching an album with a link to the album's page
@app.route('/api/search_album', methods=['GET'])
def api_search_album():
    album_title = request.args.get('album_title')
    print(f"Received album_title: {album_title}")  # Debugging log

    if album_title:
        query = text("""
                     SELECT albumBelong.*, Artist.Name AS ArtistName
                     FROM albumBelong
                     JOIN Artist ON albumBelong.ArtistID = Artist.ArtistID
                     WHERE LOWER(TRIM(Title)) = LOWER(TRIM(:album_title))
                     """)
        result = g.conn.execute(query, {'album_title': album_title}).fetchall()
        print(f"Query result: {result}")  # Debugging log
    else:
        result = []
        print("No album_title provided.")  # Debugging log

    # Format the response for React
    albums = [{
        "id": album[0].strip(),
        "title": album[1].strip(),
        "releaseYear": album[2],
        "genre": album[3],
        "artist": album[5].strip()
    } for album in result]

    print(f"Albums response: {albums}")  # Debugging log
    return jsonify({"albums": albums})




# Routes for displaying the album's page
@app.route('/album/<album_id>')
def album_details(album_id):
    return render_template('album_details.html')

@app.route('/api/album/<album_id>')
def api_album_details(album_id):
    album_query = text("""
        SELECT albumBelong.*, Artist.Name AS ArtistName, Artist.ArtistID, Genre.GenreID, Genre.Name AS GenreName
        FROM albumBelong
        JOIN Artist ON albumBelong.ArtistID = Artist.ArtistID
        JOIN belongsTo2 ON Artist.ArtistID = belongsTo2.ArtistID
        JOIN Genre ON belongsTo2.GenreID = Genre.GenreID
        WHERE albumBelong.AlbumID = :album_id
    """)
    album = g.conn.execute(album_query, {'album_id': album_id}).fetchone()

    songs_query = text("""
        SELECT song.* FROM song
        JOIN contains2 ON song.songID = contains2.songID
        WHERE contains2.AlbumID = :album_id
    """)
    songs = g.conn.execute(songs_query, {'album_id': album_id}).fetchall()

    if album:
        # Adjust indices based on your database schema
        album_details = {
            "title": album[1],
            "releaseYear": album[2],
            "genreId": album[-2].strip(),  # Ensure the correct index for GenreID
            "genreName": album[-1],        # Ensure the correct index for GenreName
            "artistId": album[4].strip(),
            "artistName": album[5]
        }
        song_details = [{"id": song[0].strip(), "title": song[1], "duration": song[3]} for song in songs]
        return jsonify({"album": album_details, "songs": song_details})
    else:
        return jsonify({"error": "Album not found"}), 404




# Route for searching an artist with a link to the artist's page
@app.route('/search_artist')
def search_artist():
    artist_name = request.args.get('artist_name')
    # Fetches artists with matching artist_name
    if artist_name:
        query = text("""
                     SELECT * FROM Artist WHERE Name LIKE :artist_name
                     """)
        result = g.conn.execute(query, {'artist_name': f'%{artist_name}%'}).fetchall()
    else:
        result = []

    return render_template('search_artist.html', artists=result)

# Route for displaying the artist's page
@app.route('/api/search_artist', methods=['GET'])
def api_search_artist():
    artist_name = request.args.get('artist_name')
    print(f"Received artist_name: {artist_name}")  # Debugging log

    if artist_name:
        query = text("""
                     SELECT * FROM Artist WHERE Name ILIKE :artist_name
                     """)
        result = g.conn.execute(query, {'artist_name': f'%{artist_name}%'}).fetchall()
        print(f"Query result: {result}")  # Debugging log
    else:
        result = []
        print("No artist_name provided.")  # Debugging log

    # Format the response for React
    artists = [{
        "id": artist[0].strip(),
        "name": artist[1].strip(),
        "biography": artist[2]
    } for artist in result]

    print(f"Artists response: {artists}")  # Debugging log
    return jsonify({"artists": artists})



# Route for displaying artists' pages.
@app.route('/api/artist/<artist_id>', methods=['GET'])
def api_artist_details(artist_id):
    # Fetch artist details
    artist_query = text("""
        SELECT Artist.*, Genre.Name AS GenreName, Genre.GenreID
        FROM Artist
        JOIN belongsTo2 ON Artist.ArtistID = belongsTo2.ArtistID
        JOIN Genre ON belongsTo2.GenreID = Genre.GenreID
        WHERE Artist.ArtistID = :artist_id
    """)
    artist = g.conn.execute(artist_query, {'artist_id': artist_id}).fetchone()

    # Fetch albums by artist
    albums_query = text("""
        SELECT * FROM albumBelong WHERE ArtistID = :artist_id
    """)
    albums = g.conn.execute(albums_query, {'artist_id': artist_id}).fetchall()

    # Fetch songs by artist
    songs_query = text("""
        SELECT Song.* FROM Song
        JOIN contains2 ON Song.songID = contains2.songID
        JOIN albumBelong ON contains2.AlbumID = albumBelong.AlbumID
        WHERE albumBelong.ArtistID = :artist_id
    """)
    songs = g.conn.execute(songs_query, {'artist_id': artist_id}).fetchall()

    if artist:
        artist_details = {
            "id": artist[0].strip(),
            "name": artist[1],
            "biography": artist[2],
            "genreId": artist[4].strip(),
            "genreName": artist[3]
        }
        album_details = [
            {"id": album[0].strip(), "title": album[1], "releaseYear": album[2]} for album in albums
        ]
        song_details = [
            {"id": song[0].strip(), "title": song[1], "genre": song[2]} for song in songs
        ]
        return jsonify({"artist": artist_details, "albums": album_details, "songs": song_details})
    else:
        return jsonify({"error": "Artist not found"}), 404



# Route for searching a genre with a link to the genre's page
@app.route('/api/search_genre', methods=['GET'])
def api_search_genre():
    print("Reached /api/search_genre route")  # Add this debug log
    genre_name = request.args.get('genre_name')
    print(f"Received genre_name: {genre_name}")  # Log received parameter
    print(f"Received genre_name: {genre_name}")  # Debugging log

    if genre_name:
        query = text("""
                     SELECT * FROM Genre
                     WHERE Name ILIKE :genre_name
                     """)
        result = g.conn.execute(query, {'genre_name': f'%{genre_name}%'}).fetchall()
        print(f"Query result: {result}")  # Debugging log
    else:
        result = []
        print("No genre_name provided.")  # Debugging log

    # Format the response for React
    genres = [{
        "id": genre[0].strip(),
        "name": genre[1].strip(),
        "description": genre[2].strip()
    } for genre in result]

    print(f"Genres response: {genres}")  # Debugging log
    return jsonify({"genres": genres})


# Route for displaying the genre's page
@app.route('/api/genre/<genre_id>', methods=['GET'])
def api_genre_details(genre_id):
    # Fetch genre details
    genre_query = text("""
        SELECT * FROM Genre WHERE GenreID = :genre_id
    """)
    genre = g.conn.execute(genre_query, {'genre_id': genre_id}).fetchone()

    # Fetch artists in the genre
    artists_query = text("""
        SELECT Artist.* FROM Artist
        JOIN belongsTo2 ON Artist.ArtistID = belongsTo2.ArtistID
        WHERE belongsTo2.GenreID = :genre_id
    """)
    artists = g.conn.execute(artists_query, {'genre_id': genre_id}).fetchall()

    # Fetch albums in the genre
    albums_query = text("""
        SELECT albumBelong.* FROM albumBelong
        WHERE albumBelong.Genre = (SELECT Name FROM Genre WHERE GenreID = :genre_id)
    """)
    albums = g.conn.execute(albums_query, {'genre_id': genre_id}).fetchall()

    # Fetch songs in the genre
    songs_query = text("""
        SELECT Song.* FROM Song
        JOIN contains2 ON Song.songID = contains2.songID
        JOIN albumBelong ON contains2.AlbumID = albumBelong.AlbumID
        WHERE albumBelong.Genre = (SELECT Name FROM Genre WHERE GenreID = :genre_id)
    """)
    songs = g.conn.execute(songs_query, {'genre_id': genre_id}).fetchall()

    if genre:
        genre_details = {
            "id": genre[0].strip(),
            "name": genre[1],
            "description": genre[2]
        }
        artist_details = [
            {"id": artist[0].strip(), "name": artist[1]} for artist in artists
        ]
        album_details = [
            {"id": album[0].strip(), "title": album[1]} for album in albums
        ]
        song_details = [
            {"id": song[0].strip(), "title": song[1], "duration": song[3]} for song in songs
        ]
        return jsonify({
            "genre": genre_details,
            "artists": artist_details,
            "albums": album_details,
            "songs": song_details
        })
    else:
        return jsonify({"error": "Genre not found"}), 404

@app.route('/api/search_playlist', methods=['GET'])
def api_search_playlist():
    playlist_title = request.args.get('playlist_title')
    print(f"Received playlist_title: {playlist_title}")  # Debugging log

    if playlist_title:
        query = text("""
                     SELECT * FROM Playlist
                     WHERE Title ILIKE :playlist_title
                     """)
        result = g.conn.execute(query, {'playlist_title': f'%{playlist_title}%'}).fetchall()
        print(f"Query result: {result}")  # Debugging log
    else:
        result = []
        print("No playlist_title provided.")  # Debugging log

    # Format the response for React
    playlists = [{
        "id": playlist[0].strip(),
        "title": playlist[1].strip(),
        "description": playlist[2].strip(),
        "creationYear": playlist[3]
    } for playlist in result]

    print(f"Playlists response: {playlists}")  # Debugging log
    return jsonify({"playlists": playlists})


# Route for displaying playlists.
@app.route('/api/playlist/<playlist_id>', methods=['GET'])
def api_playlist_details(playlist_id):
    # Fetch playlist details
    playlist_query = text("""
                          SELECT * FROM Playlist
                          WHERE PlaylistID = :playlist_id
                          """)
    playlist = g.conn.execute(playlist_query, {'playlist_id': playlist_id}).fetchone()

    # Fetch songs in the playlist
    songs_query = text("""
                       SELECT Song.* FROM Song
                       JOIN contains1 ON Song.songID = contains1.songID
                       WHERE contains1.PlaylistID = :playlist_id
                       """)
    songs = g.conn.execute(songs_query, {'playlist_id': playlist_id}).fetchall()

    # Fetch the creator of the playlist
    creator_query = text("""
                         SELECT Users.* FROM Users
                         JOIN CreateORFollow ON Users.UserID = CreateORFollow.UserID
                         WHERE CreateORFollow.PlaylistID = :playlist_id AND CreateORFollow.Creates = TRUE
                         """)
    creator = g.conn.execute(creator_query, {'playlist_id': playlist_id}).fetchone()

    # Fetch the users who follow the playlist
    followers_query = text("""
                           SELECT Users.* FROM Users
                           JOIN CreateORFollow ON Users.UserID = CreateORFollow.UserID
                           WHERE CreateORFollow.PlaylistID = :playlist_id AND CreateORFollow.Creates = FALSE
                           """)
    followers = g.conn.execute(followers_query, {'playlist_id': playlist_id}).fetchall()

    if playlist:
        playlist_details = {
            "id": playlist[0].strip(),
            "title": playlist[1],
            "description": playlist[2],
            "creationYear": playlist[3],
            "creator": {"id": creator[0].strip(), "name": creator[1]} if creator else None,
            "followers": [{"id": follower[0].strip(), "name": follower[1]} for follower in followers],
            "songs": [{"id": song[0].strip(), "title": song[1], "duration": song[3]} for song in songs]
        }
        return jsonify(playlist_details)
    else:
        return jsonify({"error": "Playlist not found"}), 404



@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.json
    print(f"Login payload: {data}")  # Debugging log

    username = data.get('username', '').strip()
    password = data.get('password', '').strip()

    if not username or not password:
        return jsonify({"success": False, "message": "Username or password is missing"}), 400

    user_query = text("SELECT * FROM Users WHERE UserName = :username AND Password = :password")
    user = g.conn.execute(user_query, {'username': username, 'password': password}).fetchone()

    if user:
        session['username'] = username  # Save username in session
        print(f"User logged in: {username}")  # Debugging log
        return jsonify({"success": True, "message": "Login successful", "username": username})
    else:
        print("Invalid login attempt")  # Debugging log
        return jsonify({"success": False, "message": "Invalid username or password"}), 401




# Route for logging out
@app.route('/api/logout', methods=['POST'])
def api_logout():
    session.pop('username', None)  # Clear the session
    return jsonify({"message": "Logged out successfully"}), 200


# Route for displaying the user's profile after logging in
@app.route('/api/profile/<username>', methods=['GET'])
def api_profile(username):
    user_query = text("SELECT * FROM Users WHERE UserName = :username")
    user = g.conn.execute(user_query, {'username': username}).fetchone()

    if user:
        # Corrected indices based on your schema
        username = user[0]  # First column is username
        email = user[1]     # Second column is email
        user_id = user[3]   # Fourth column is userID

        # Fetch songs listened to by the user
        listens_to_query = text("""
            SELECT Song.songID, Song.Title, Song.Genre 
            FROM listensTO
            JOIN Song ON listensTO.songID = Song.songID
            WHERE listensTO.userID = :user_id
        """)
        songs = g.conn.execute(listens_to_query, {'user_id': user_id}).fetchall()

        # Fetch artists followed by the user
        follows_query = text("""
            SELECT Artist.ArtistID, Artist.Name, follows.FollowDate
            FROM follows
            JOIN Artist ON follows.artistID = Artist.artistID
            WHERE follows.userID = :user_id
        """)
        artists = g.conn.execute(follows_query, {'user_id': user_id}).fetchall()

        # Fetch playlists created by the user
        created_playlists_query = text("""
            SELECT Playlist.PlaylistID, Playlist.Title 
            FROM createORfollow
            JOIN Playlist ON createORfollow.PlaylistID = Playlist.PlaylistID
            WHERE createORfollow.userID = :user_id AND createORfollow.creates = TRUE
        """)
        created_playlists = g.conn.execute(created_playlists_query, {'user_id': user_id}).fetchall()

        # Fetch playlists followed by the user
        followed_playlists_query = text("""
            SELECT Playlist.PlaylistID, Playlist.Title 
            FROM createORfollow
            JOIN Playlist ON createORfollow.PlaylistID = Playlist.PlaylistID
            WHERE createORfollow.userID = :user_id AND createORfollow.creates = FALSE
        """)
        followed_playlists = g.conn.execute(followed_playlists_query, {'user_id': user_id}).fetchall()

        # Format response
        return jsonify({
            "user": {"username": username, "email": email},
            "songs": [{"id": song[0], "title": song[1], "genre": song[2]} for song in songs],
            "artists": [{"id": artist[0], "name": artist[1], "followDate": artist[2]} for artist in artists],
            "createdPlaylists": [{"id": playlist[0], "title": playlist[1]} for playlist in created_playlists],
            "followedPlaylists": [{"id": playlist[0], "title": playlist[1]} for playlist in followed_playlists],
        })
    else:
        return jsonify({"error": "User not found"}), 404






    
# Route for the recommended songs button on the user's profile page
# Route for the recommended songs button on the user's profile page
@app.route('/api/recommendations/<username>', methods=['GET'])
def api_recommendations(username):
    user_query = text("SELECT TRIM(userID) FROM Users WHERE UserName = :username")
    user = g.conn.execute(user_query, {'username': username}).fetchone()

    if not user:
        return jsonify({"error": "User not found"}), 404

    user_id = user[0]
    
    # Fetch listened songs
    listened_songs_query = text("""
        SELECT TRIM(songID)
        FROM listensTO
        WHERE TRIM(userID) = :user_id
    """)
    listened_song_ids = [song[0] for song in g.conn.execute(listened_songs_query, {'user_id': user_id}).fetchall()]

    # Fetch followed genres
    genre_query = text("""
        SELECT DISTINCT TRIM(Genre.Name)
        FROM Artist
        JOIN follows ON TRIM(Artist.ArtistID) = TRIM(follows.ArtistID)
        JOIN belongsTo2 ON TRIM(Artist.ArtistID) = TRIM(belongsTo2.ArtistID)
        JOIN Genre ON TRIM(belongsTo2.GenreID) = TRIM(Genre.GenreID)
        WHERE TRIM(follows.userID) = :user_id
    """)
    followed_genres = [genre[0] for genre in g.conn.execute(genre_query, {'user_id': user_id}).fetchall()]

    if not followed_genres:
        return jsonify({"songs": [], "message": "No followed genres"}), 200

    # Fetch recommendations
    recommended_songs = []
    for genre_name in followed_genres:
        song_query = text("""
            SELECT Song.songID, Song.Title, Song.Genre, Artist.Name AS ArtistName
            FROM Song
            JOIN contains2 ON Song.songID = contains2.songID
            JOIN albumBelong ON contains2.AlbumID = albumBelong.AlbumID
            JOIN Artist ON albumBelong.ArtistID = Artist.ArtistID
            WHERE Song.Genre = :genre
            AND Song.songID NOT IN :listened_song_ids
            LIMIT 5
        """)
        songs = g.conn.execute(song_query, {
            'genre': genre_name,
            'listened_song_ids': tuple(listened_song_ids) if listened_song_ids else ('',)
        }).fetchall()
        recommended_songs.extend(songs)

    return jsonify({
        "songs": [{"id": song[0], "title": song[1], "genre": song[2], "artist": song[3]} for song in recommended_songs]
    })




# Route for the recommended artists button on the user's profile page
@app.route('/recommend_artists/<username>', methods=['GET'])
def recommend_artists(username):
    print(f"Username for recommendations: '{username}'")

    # Get the user_id
    user_query = text("SELECT userID FROM Users WHERE UserName = :username")
    user = g.conn.execute(user_query, {'username': username}).fetchone()

    if not user:
        print(f"User {username} not found in Users table")
        return jsonify({"error": "User not found"}), 404

    user_id = user[0]
    print(f"User ID for recommendations: '{user_id}'")

    # Get genres the user follows
    genre_query = text("""
        SELECT DISTINCT Genre.GenreID
        FROM Artist
        JOIN follows ON Artist.ArtistID = follows.ArtistID
        JOIN belongsTo2 ON Artist.ArtistID = belongsTo2.ArtistID
        JOIN Genre ON belongsTo2.GenreID = Genre.GenreID
        WHERE follows.userID = :user_id
    """)
    followed_genres = g.conn.execute(genre_query, {'user_id': user_id}).fetchall()

    if not followed_genres:
        print(f"No genres followed by user {user_id}")
        return jsonify({"message": "No genres found for this user", "artists": []}), 200

    print(f"Genres followed by User {user_id}: {followed_genres}")

    # Get artists not followed by the user
    recommended_artists = []
    for genre in followed_genres:
        genre_id = genre[0].strip()

        print(f"Processing Genre ID: {genre_id}")

        artist_query = text("""
            SELECT DISTINCT Artist.ArtistID, Artist.Name, Artist.Biography
            FROM Artist
            JOIN belongsTo2 ON Artist.ArtistID = belongsTo2.ArtistID
            WHERE belongsTo2.GenreID = :genre_id
            AND NOT EXISTS (
                SELECT 1 FROM follows
                WHERE follows.ArtistID = Artist.ArtistID AND follows.userID = :user_id
            )
            LIMIT 5
        """)
        artists = g.conn.execute(artist_query, {'genre_id': genre_id, 'user_id': user_id}).fetchall()

        if not artists:
            print(f"No artists found for Genre ID: {genre_id}")
        else:
            print(f"Artists found for Genre ID {genre_id}: {artists}")

        for artist in artists:
            recommended_artists.append({
                "id": artist[0].strip(),  # Artist ID
                "name": artist[1],  # Artist Name
                "biography": artist[2]  # Artist Biography
            })

    print(f"Final Recommended Artists: {recommended_artists}")
    return jsonify({"artists": recommended_artists})








#Route for the recommended playlists button on the user's profile page
# Route for the recommended playlists button on the user's profile page
@app.route('/recommend_playlists/<username>', methods=['GET'])
def recommend_playlists(username):
    print(f"Username for playlist recommendations: '{username}'")

    # Step 1: Get the user_id
    user_query = text("SELECT userID FROM Users WHERE UserName = :username")
    user = g.conn.execute(user_query, {'username': username}).fetchone()

    if not user:
        print(f"User {username} not found in Users table")
        return jsonify({"error": "User not found"}), 404

    user_id = user[0]
    print(f"User ID for playlist recommendations: '{user_id}'")

    # Step 2: Fetch followed artists
    artist_query = text("SELECT ArtistID FROM follows WHERE userID = :user_id")
    followed_artists = g.conn.execute(artist_query, {'user_id': user_id}).fetchall()
    artist_ids = [artist[0] for artist in followed_artists]

    if not artist_ids:
        print(f"No artists followed for user {user_id}")
        return jsonify({"message": "No followed artists, no playlist recommendations available", "playlists": []}), 200

    print(f"Followed artists for user {user_id}: {artist_ids}")

    # Step 3: Fetch recommended playlists
    playlist_query = text("""
        SELECT DISTINCT Playlist.PlaylistID, Playlist.Title
        FROM Playlist
        JOIN contains1 ON Playlist.PlaylistID = contains1.PlaylistID
        JOIN contains2 ON contains1.songID = contains2.songID
        JOIN albumBelong ON contains2.AlbumID = albumBelong.AlbumID
        WHERE albumBelong.ArtistID IN :artist_ids
    """)
    playlists = g.conn.execute(playlist_query, {'artist_ids': tuple(artist_ids)}).fetchall()

    recommended_playlists = [{"id": playlist[0].strip(), "title": playlist[1]} for playlist in playlists]
    print(f"Recommended playlists for user {user_id}: {recommended_playlists}")

    return jsonify({"playlists": recommended_playlists})


    

if __name__ == "__main__":
  import click

  @click.command()
  @click.option('--debug', is_flag=True)
  @click.option('--threaded', is_flag=True)
  @click.argument('HOST', default='0.0.0.0')
  @click.argument('PORT', default=8111, type=int)
  def run(debug, threaded, host, port):
    """
    This function handles command line parameters.
    Run the server using:

        python3 server.py

    Show the help text using:

        python3 server.py --help

    """

    HOST, PORT = host, port
    print("running on %s:%d" % (HOST, PORT))
    app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)

  run()