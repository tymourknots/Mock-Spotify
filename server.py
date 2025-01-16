import os
  # accessible as a variable in index.html:
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response, abort, session, url_for, jsonify, send_from_directory
from flask_cors import CORS


tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, static_folder='static')
app.secret_key = os.urandom(24)
CORS(app)


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
def get_session_data():
    """
    Return session data for the logged-in user.
    """
    username = session.get('username', None)
    return jsonify({'username': username})



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
@app.route('/genre/<genre_id>')
def genre_details(genre_id):
    # Fetch genre details
    genre_query = text("""
                       SELECT * FROM Genre WHERE GenreID = :genre_id
                       """)
    genre_details = g.conn.execute(genre_query, {'genre_id': genre_id}).fetchone()

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

    return render_template('genre_details.html', genre=genre_details, artists=artists, albums=albums, songs=songs)

#Route for searching a playlist with a link to the playlist's page
@app.route('/api/search_playlist', methods=['GET'])
def api_search_playlist():
    playlist_title = request.args.get('playlist_title')

    if playlist_title:
        query = text("""
                     SELECT * FROM Playlist
                     WHERE Title ILIKE :playlist_title
                     """)
        result = g.conn.execute(query, {'playlist_title': f'%{playlist_title}%'}).fetchall()
    else:
        result = []

    # Format the response for React
    playlists = [{
        "id": playlist[0].strip(),
        "title": playlist[1].strip(),
        "description": playlist[2].strip(),
        "creationYear": playlist[3]
    } for playlist in result]

    return jsonify({"playlists": playlists})


# Route for logging in
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password'].strip()

        # Check if the username and password match a user in the database
        user_query = text("SELECT * FROM Users WHERE UserName = :username AND Password = :password")
        user = g.conn.execute(user_query, {'username': username, 'password': password}).fetchone()

        if user:
            session['username'] = username  
            return redirect(url_for('index'))
        else:
            return redirect(url_for('login'))

    return render_template('login.html')

# Route for logging out
@app.route('/logout')
def logout():
    # Remove the username from the session
    session.pop('username', None)  
    return redirect(url_for('index'))

# Route for displaying the user's profile after logging in
@app.route('/profile/<username>')
def profile(username):
    if 'username' in session and session['username'] == username:
        user_query = text("SELECT * FROM Users WHERE UserName = :username")
        user = g.conn.execute(user_query, {'username': username}).fetchone()

        if user:
            user_id = user[3]  # Extract userID
            print(f"User ID: {user_id} for username: {username}")

            # Listened Songs
            listens_to_query = text("""
                SELECT Song.* FROM Song
                JOIN listensTO ON Song.songID = listensTO.songID
                WHERE listensTO.userid = :user_id
            """)
            listened_songs = g.conn.execute(listens_to_query, {'user_id': user_id}).fetchall()

            # Followed Artists
            followed_artists_query = text("""
                SELECT Artist.*, follows.FollowDate
                FROM follows
                JOIN Artist ON follows.artistID = Artist.artistID
                WHERE follows.userid = :user_id
            """)
            followed_artists = g.conn.execute(followed_artists_query, {'user_id': user_id}).fetchall()

            # Created Playlists
            created_playlists_query = text("""
                SELECT Playlist.* FROM Playlist
                JOIN createORfollow ON Playlist.PlaylistID = createORfollow.PlaylistID
                WHERE createORfollow.userid = :user_id AND createORfollow.creates = TRUE
            """)
            created_playlists = g.conn.execute(created_playlists_query, {'user_id': user_id}).fetchall()

            # Followed Playlists
            followed_playlists_query = text("""
                SELECT Playlist.* FROM Playlist
                JOIN createORfollow ON Playlist.PlaylistID = createORfollow.PlaylistID
                WHERE createORfollow.userid = :user_id AND createORfollow.creates = FALSE
            """)
            followed_playlists = g.conn.execute(followed_playlists_query, {'user_id': user_id}).fetchall()

            return render_template('profile.html', user=user, songs=listened_songs, artists=followed_artists, created_playlists=created_playlists, followed_playlists=followed_playlists)
        else:
            return "User not found", 404
    else:
        return redirect(url_for('login'))

    
# Route for the recommended songs button on the user's profile page
# Route for the recommended songs button on the user's profile page
@app.route('/recommendations/<username>')
def recommendations(username):
    print(f"Username for recommendations: '{username}' (Type: {type(username)})")  # Debug log

    # 🔥 Step 1: Get the user_id from the Users table
    user_query = text("SELECT TRIM(userID) FROM Users WHERE UserName = :username")
    user = g.conn.execute(user_query, {'username': username}).fetchone()
    
    if not user:
        print(f"User {username} not found in Users table")
        return "User not found"
    
    user_id = user[0]  # Extract user_id and trim
    print(f"User ID for recommendations: '{user_id}' (Type: {type(user_id)})")  # Debug log

    # 🔥 Step 2: Get the songs the user has already listened to
    listened_songs_query = text("""
        SELECT TRIM(songID)
        FROM listensTO
        WHERE TRIM(userID) = :user_id
    """)
    listened_song_ids = [song[0] for song in g.conn.execute(listened_songs_query, {'user_id': user_id}).fetchall()]
    print(f"Listened songs for user {user_id}: {listened_song_ids}")  # Debug log

    # 🔥 Step 3: Get the genres the user follows
    genre_query = text("""
        SELECT DISTINCT TRIM(Genre.Name)
        FROM Artist
        JOIN follows ON TRIM(Artist.ArtistID) = TRIM(follows.ArtistID)
        JOIN belongsTo2 ON TRIM(Artist.ArtistID) = TRIM(belongsTo2.ArtistID)
        JOIN Genre ON TRIM(belongsTo2.GenreID) = TRIM(Genre.GenreID)
        WHERE TRIM(follows.userID) = :user_id
    """)
    followed_genres = g.conn.execute(genre_query, {'user_id': user_id}).fetchall()
    print(f"Genres followed by User {user_id}: {followed_genres}")  # Debug log

    if not followed_genres:
        print(f"No genres found for user {user_id}")
        return "No genres found for this user"

    # 🔥 Step 4: Get songs in those genres that the user has NOT listened to
    recommended_songs = []
    for genre in followed_genres:
        genre_name = genre[0].strip()
        if not genre_name:
            continue

        print(f"Processing Genre: {genre_name}")  # Debug log

        song_query = text("""
            SELECT *
            FROM (
                SELECT Song.*, TRIM(Artist.Name) AS ArtistName, TRIM(Artist.ArtistID)
                FROM Song
                JOIN contains2 ON TRIM(Song.songID) = TRIM(contains2.songID)
                JOIN albumBelong ON TRIM(contains2.AlbumID) = TRIM(albumBelong.AlbumID)
                JOIN Artist ON TRIM(albumBelong.ArtistID) = TRIM(Artist.ArtistID)
                WHERE TRIM(Song.Genre) = :genre
                AND TRIM(Song.songID) NOT IN :listened_song_ids
            ) AS distinct_songs
            ORDER BY RANDOM()
            LIMIT 5
        """)

        songs = g.conn.execute(song_query, {
            'genre': genre_name,
            'listened_song_ids': tuple(listened_song_ids) if listened_song_ids else ('',)  # Avoid empty IN clause
        }).fetchall()
        
        print(f"Songs recommended for User {user_id} in Genre {genre_name}: {songs}")  # Debug log
        recommended_songs.extend(songs)

    return render_template('recommendations.html', songs=recommended_songs)




# Route for the recommended artists button on the user's profile page
@app.route('/recommend_artists/<username>')
def recommend_artists(username):
    print(f"Username for recommendations: '{username}' (Type: {type(username)})")  # Debug log

    # 🔥 Step 1: Get the user_id from the Users table
    user_query = text("SELECT TRIM(userID) FROM Users WHERE UserName = :username")
    user = g.conn.execute(user_query, {'username': username}).fetchone()
    
    if not user:
        print(f"User {username} not found in Users table")
        return "User not found"
    
    user_id = user[0].strip()  # Remove whitespace
    print(f"User ID for recommendations: '{user_id}' (Type: {type(user_id)})")  # Debug log
    
    # 🔥 Step 2: Get genres the user follows
    genre_query = text("""
        SELECT DISTINCT TRIM(Genre.GenreID)
        FROM Artist
        JOIN follows ON TRIM(Artist.ArtistID) = TRIM(follows.ArtistID)
        JOIN belongsTo2 ON TRIM(Artist.ArtistID) = TRIM(belongsTo2.ArtistID)
        JOIN Genre ON TRIM(belongsTo2.GenreID) = TRIM(Genre.GenreID)
        WHERE TRIM(follows.userID) = :user_id
    """)
    followed_genres = g.conn.execute(genre_query, {'user_id': user_id}).fetchall()
    print(f"Genres Followed for User {user_id}: {followed_genres}")  # Debug log

    if not followed_genres:
        print(f"No genres found for user {user_id}")
        return "No genres found for this user"

    # 🔥 Step 3: Get artists in those genres that the user does not follow
    recommended_artists = []
    for genre in followed_genres:
        if not genre[0]:
            continue

        print(f"Processing Genre: {genre[0]}")  # Debug log
        artist_query = text("""
            SELECT DISTINCT Artist.*
            FROM Artist
            JOIN belongsTo2 ON TRIM(Artist.ArtistID) = TRIM(belongsTo2.ArtistID)
            WHERE TRIM(belongsTo2.GenreID) = :genre_id 
            AND NOT EXISTS (
                SELECT 1 FROM Follows 
                WHERE TRIM(Follows.ArtistID) = TRIM(Artist.ArtistID) 
                AND TRIM(Follows.userID) = :user_id
            )
            LIMIT 5
        """)
        
        artists = g.conn.execute(artist_query, {'genre_id': genre[0].strip(), 'user_id': user_id}).fetchall()
        print(f"Artists recommended for User {user_id} in Genre {genre[0].strip()}: {artists}")  # Debug log

        recommended_artists.extend(artists)

    return render_template('recommend_artists.html', artists=recommended_artists)





#Route for the recommended playlists button on the user's profile page
# Route for the recommended playlists button on the user's profile page
@app.route('/recommend_playlists/<username>')
def recommend_playlists(username):
    print(f"Username for playlist recommendations: '{username}' (Type: {type(username)})")  # Debug log

    # 🔥 Step 1: Get the user_id from the Users table
    user_query = text("SELECT TRIM(userID) FROM Users WHERE UserName = :username")
    user = g.conn.execute(user_query, {'username': username}).fetchone()
    
    if not user:
        print(f"User {username} not found in Users table")
        return "User not found"
    
    user_id = user[0]  # Extract user_id and trim
    print(f"User ID for playlist recommendations: '{user_id}' (Type: {type(user_id)})")  # Debug log

    # 🔥 Step 2: Fetch the artists followed by the user
    artist_query = text("""
        SELECT TRIM(ArtistID) 
        FROM follows 
        WHERE TRIM(userID) = :user_id
    """)
    followed_artists = g.conn.execute(artist_query, {'user_id': user_id}).fetchall()
    print(f"Followed Artists for User {user_id}: {followed_artists}")  # Debug log

    # 🔥 Step 3: Convert followed artists to a list of artist IDs
    artist_ids = [artist[0].strip() for artist in followed_artists]

    if not artist_ids:
        print(f"No artists followed for user {user_id}")
        return "No artists followed, so no playlist recommendations available."

    # 🔥 Step 4: Fetch playlists that contain songs by these artists
    playlist_query = text("""
        SELECT DISTINCT Playlist.PlaylistID, Playlist.Title
        FROM Playlist
        JOIN contains1 ON TRIM(Playlist.PlaylistID) = TRIM(contains1.PlaylistID)
        JOIN contains2 ON TRIM(contains1.songID) = TRIM(contains2.songID)
        JOIN albumBelong ON TRIM(contains2.AlbumID) = TRIM(albumBelong.AlbumID)
        WHERE TRIM(albumBelong.ArtistID) IN :artist_ids
    """)
    playlists = g.conn.execute(playlist_query, {'artist_ids': tuple(artist_ids)}).fetchall()
    print(f"Playlists for User {user_id}: {playlists}")  # Debug log

    # 🔥 Step 5: Render the recommended playlists
    return render_template('recommend_playlists.html', playlists=playlists)



#Route for displaying the playlist's page
@app.route('/playlist/<playlist_id>')
def playlist_details(playlist_id):
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
        return render_template('playlist_details.html', playlist=playlist, songs=songs, creator=creator, followers=followers)
    else:
        return "Playlist not found", 404
    

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
