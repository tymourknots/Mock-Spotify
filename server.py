import os
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
    """
    Search for a song by its title or ID, and retrieve associated playlists.

    Query Parameters:
        - song_title (str, optional): The title of the song to search for.
        - song_id (str, optional): The unique ID of the song to search for.

    Returns:
        - JSON response containing:
            - "songs": A list of matching songs with details such as album, artist, genre, duration, release year, and plays.
            - "playlists": A list of playlists that include the specified song.
            - "error": An error message if neither song_title nor song_id is provided.
    """
    # Get query parameters and trim whitespace
    song_title = request.args.get('song_title', '').strip()
    song_id = request.args.get('song_id', '').strip()

    # If both parameters are missing, return an error response
    if not song_id and not song_title:
        return jsonify({"songs": [], "playlists": [], "error": "No song ID or title provided"}), 400

    result = []  # Stores matching song details
    playlists = []  # Stores playlists containing the song

    # Execute the query only if at least one parameter is provided
    if song_id or song_title:
        # Query to fetch song details and associated album/artist information
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
        result = g.conn.execute(query, {
            'song_id': song_id or None,
            'song_title': f"%{song_title}%" if song_title else None
        }).fetchall()

        # If searching by title and results are found, use the first song's ID for further queries
        if result and not song_id:
            song_id = result[0][0]  # Extract the song ID

        # If a song ID is available, fetch playlists containing the song
        if song_id:
            playlist_query = text("""
                SELECT Playlist.* FROM Playlist
                JOIN contains1 ON Playlist.PlaylistID = contains1.PlaylistID
                WHERE contains1.songID = :song_id
            """)
            playlists = g.conn.execute(playlist_query, {'song_id': song_id}).fetchall()

    # Format the song details into a list of dictionaries
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

    # Format the playlists into a list of dictionaries
    playlists_data = [{"id": playlist[0].strip(), "title": playlist[1]} for playlist in playlists]

    # Return the songs and playlists in a JSON response
    return jsonify({"songs": songs, "playlists": playlists_data})






# Route for searching an album with a link to the album's page
@app.route('/api/search_album', methods=['GET'])
def api_search_album():
    """
    Search for an album by its title.

    Query Parameters:
        - album_title (str, optional): The title of the album to search for.

    Returns:
        - JSON response containing:
            - "albums": A list of albums with details such as ID, title, release year, genre, and artist.
            - If no album_title is provided, returns an empty "albums" list.
    """
    # Get the album title from query parameters
    album_title = request.args.get('album_title')

    # Initialize the result list
    result = []

    # If album_title is provided, execute the query
    if album_title:
        query = text("""
            SELECT albumBelong.*, Artist.Name AS ArtistName
            FROM albumBelong
            JOIN Artist ON albumBelong.ArtistID = Artist.ArtistID
            WHERE LOWER(TRIM(Title)) = LOWER(TRIM(:album_title))
        """)
        result = g.conn.execute(query, {'album_title': album_title}).fetchall()

    # Format the query result into a list of dictionaries
    albums = [{
        "id": album[0].strip(),
        "title": album[1].strip(),
        "releaseYear": album[2],
        "genre": album[3],
        "artist": album[5].strip()
    } for album in result]

    # Return the formatted albums data as JSON
    return jsonify({"albums": albums})




# Routes for displaying the album's page
@app.route('/api/album/<album_id>')
def api_album_details(album_id):
    """
    Fetch detailed information about an album and its associated songs.

    Path Parameters:
        - album_id (str): The unique identifier of the album.

    Returns:
        - JSON response containing:
            - "album": A dictionary with album details such as title, release year, genre, and artist information.
            - "songs": A list of songs in the album, including their ID, title, and duration.
        - If the album is not found, returns an error message with a 404 status code.
    """
    # Query to fetch album details, including artist and genre
    album_query = text("""
        SELECT albumBelong.*, Artist.Name AS ArtistName, Artist.ArtistID, Genre.GenreID, Genre.Name AS GenreName
        FROM albumBelong
        JOIN Artist ON albumBelong.ArtistID = Artist.ArtistID
        JOIN belongsTo2 ON Artist.ArtistID = belongsTo2.ArtistID
        JOIN Genre ON belongsTo2.GenreID = Genre.GenreID
        WHERE albumBelong.AlbumID = :album_id
    """)
    album = g.conn.execute(album_query, {'album_id': album_id}).fetchone()

    # Query to fetch songs in the album
    songs_query = text("""
        SELECT song.* 
        FROM song
        JOIN contains2 ON song.songID = contains2.songID
        WHERE contains2.AlbumID = :album_id
    """)
    songs = g.conn.execute(songs_query, {'album_id': album_id}).fetchall()

    if album:
        # Format album details into a dictionary
        album_details = {
            "title": album[1],
            "releaseYear": album[2],
            "genreId": album[-2].strip(),  # Genre ID
            "genreName": album[-1],       # Genre Name
            "artistId": album[4].strip(), # Artist ID
            "artistName": album[5]        # Artist Name
        }

        # Format songs into a list of dictionaries
        song_details = [
            {"id": song[0].strip(), "title": song[1], "duration": song[3]}
            for song in songs
        ]

        # Return JSON response with album and song details
        return jsonify({"album": album_details, "songs": song_details})
    else:
        # Return error response if album is not found
        return jsonify({"error": "Album not found"}), 404



# Route for searching the artist's page
@app.route('/api/search_artist', methods=['GET'])
def api_search_artist():
    """
    Search for artists by name.

    Query Parameters:
        - artist_name (str): The name or partial name of the artist to search for.

    Returns:
        - JSON response containing:
            - "artists": A list of dictionaries, each with:
                - "id": Artist ID.
                - "name": Artist name.
                - "biography": Artist biography.
        - If no artist_name is provided, returns an empty list.
    """
    # Get the artist name from the query parameters
    artist_name = request.args.get('artist_name')

    # Initialize the result
    result = []

    if artist_name:
        # Query to search for artists whose names match the input
        query = text("""
            SELECT * 
            FROM Artist 
            WHERE Name ILIKE :artist_name
        """)
        result = g.conn.execute(query, {'artist_name': f'%{artist_name}%'}).fetchall()

    # Format the response for the frontend
    artists = [
        {
            "id": artist[0].strip(),
            "name": artist[1].strip(),
            "biography": artist[2]
        }
        for artist in result
    ]

    # Return the formatted list of artists
    return jsonify({"artists": artists})




# Route for displaying artists' pages.
@app.route('/api/artist/<artist_id>', methods=['GET'])
def api_artist_details(artist_id):
    """
    Fetch detailed information about a specific artist.

    URL Parameters:
        - artist_id (str): The unique ID of the artist.

    Returns:
        - JSON response containing:
            - "artist": Dictionary with artist details:
                - "id": Artist ID.
                - "name": Artist name.
                - "biography": Artist biography.
                - "genreId": Genre ID.
                - "genreName": Genre name.
            - "albums": List of dictionaries, each with:
                - "id": Album ID.
                - "title": Album title.
                - "releaseYear": Album release year.
            - "songs": List of dictionaries, each with:
                - "id": Song ID.
                - "title": Song title.
                - "genre": Song genre.
        - If the artist is not found, returns a 404 error with a JSON error message.
    """
    # Fetch artist details
    artist_query = text("""
        SELECT Artist.*, Genre.Name AS GenreName, Genre.GenreID
        FROM Artist
        JOIN belongsTo2 ON Artist.ArtistID = belongsTo2.ArtistID
        JOIN Genre ON belongsTo2.GenreID = Genre.GenreID
        WHERE Artist.ArtistID = :artist_id
    """)
    artist = g.conn.execute(artist_query, {'artist_id': artist_id}).fetchone()

    # Fetch albums by the artist
    albums_query = text("""
        SELECT * 
        FROM albumBelong 
        WHERE ArtistID = :artist_id
    """)
    albums = g.conn.execute(albums_query, {'artist_id': artist_id}).fetchall()

    # Fetch songs by the artist
    songs_query = text("""
        SELECT Song.* 
        FROM Song
        JOIN contains2 ON Song.songID = contains2.songID
        JOIN albumBelong ON contains2.AlbumID = albumBelong.AlbumID
        WHERE albumBelong.ArtistID = :artist_id
    """)
    songs = g.conn.execute(songs_query, {'artist_id': artist_id}).fetchall()

    if artist:
        # Format artist details
        artist_details = {
            "id": artist[0].strip(),
            "name": artist[1],
            "biography": artist[2],
            "genreId": artist[4].strip(),  # Ensure the correct index for GenreID
            "genreName": artist[3]        # Ensure the correct index for GenreName
        }

        # Format albums
        album_details = [
            {
                "id": album[0].strip(),
                "title": album[1],
                "releaseYear": album[2]
            }
            for album in albums
        ]

        # Format songs
        song_details = [
            {
                "id": song[0].strip(),
                "title": song[1],
                "genre": song[2]
            }
            for song in songs
        ]

        # Return the artist details, albums, and songs
        return jsonify({
            "artist": artist_details,
            "albums": album_details,
            "songs": song_details
        })
    else:
        # Return an error if the artist is not found
        return jsonify({"error": "Artist not found"}), 404




# Route for searching a genre with a link to the genre's page
@app.route('/api/search_genre', methods=['GET'])
def api_search_genre():
    """
    Search for genres based on a partial or full genre name.

    Query Parameters:
        - genre_name (str): The partial or full name of the genre to search for.

    Returns:
        - JSON response containing:
            - "genres": List of dictionaries, each with:
                - "id": Genre ID.
                - "name": Genre name.
                - "description": Genre description.
        - If no genre_name is provided, returns an empty list of genres.
    """
    # Get the genre name from query parameters
    genre_name = request.args.get('genre_name')

    # Query result placeholder
    result = []

    if genre_name:
        # SQL query to search for genres matching the provided name (case-insensitive)
        query = text("""
            SELECT * 
            FROM Genre
            WHERE Name ILIKE :genre_name
        """)
        # Execute the query and fetch results
        result = g.conn.execute(query, {'genre_name': f'%{genre_name}%'}).fetchall()

    # Format the result into a JSON-friendly structure
    genres = [
        {
            "id": genre[0].strip(),
            "name": genre[1].strip(),
            "description": genre[2].strip()
        }
        for genre in result
    ]

    # Return the response as JSON
    return jsonify({"genres": genres})



# Route for displaying the genre's page
@app.route('/api/genre/<genre_id>', methods=['GET'])
def api_genre_details(genre_id):
    """
    Retrieve details for a specific genre, along with associated artists, albums, and songs.

    Path Parameters:
        - genre_id (str): The ID of the genre to retrieve details for.

    Returns:
        - JSON response containing:
            - "genre": Dictionary with details about the genre:
                - "id": Genre ID.
                - "name": Genre name.
                - "description": Genre description.
            - "artists": List of dictionaries with artist details:
                - "id": Artist ID.
                - "name": Artist name.
            - "albums": List of dictionaries with album details:
                - "id": Album ID.
                - "title": Album title.
            - "songs": List of dictionaries with song details:
                - "id": Song ID.
                - "title": Song title.
                - "duration": Song duration.
        - If the genre is not found, returns a 404 error with an "error" message.
    """
    # Query to fetch genre details
    genre_query = text("""
        SELECT * FROM Genre WHERE GenreID = :genre_id
    """)
    genre = g.conn.execute(genre_query, {'genre_id': genre_id}).fetchone()

    # Query to fetch artists associated with the genre
    artists_query = text("""
        SELECT Artist.* FROM Artist
        JOIN belongsTo2 ON Artist.ArtistID = belongsTo2.ArtistID
        WHERE belongsTo2.GenreID = :genre_id
    """)
    artists = g.conn.execute(artists_query, {'genre_id': genre_id}).fetchall()

    # Query to fetch albums associated with the genre
    albums_query = text("""
        SELECT albumBelong.* FROM albumBelong
        WHERE albumBelong.Genre = (SELECT Name FROM Genre WHERE GenreID = :genre_id)
    """)
    albums = g.conn.execute(albums_query, {'genre_id': genre_id}).fetchall()

    # Query to fetch songs associated with the genre
    songs_query = text("""
        SELECT Song.* FROM Song
        JOIN contains2 ON Song.songID = contains2.songID
        JOIN albumBelong ON contains2.AlbumID = albumBelong.AlbumID
        WHERE albumBelong.Genre = (SELECT Name FROM Genre WHERE GenreID = :genre_id)
    """)
    songs = g.conn.execute(songs_query, {'genre_id': genre_id}).fetchall()

    if genre:
        # Format the genre details
        genre_details = {
            "id": genre[0].strip(),
            "name": genre[1],
            "description": genre[2]
        }

        # Format artist details
        artist_details = [
            {"id": artist[0].strip(), "name": artist[1]} for artist in artists
        ]

        # Format album details
        album_details = [
            {"id": album[0].strip(), "title": album[1]} for album in albums
        ]

        # Format song details
        song_details = [
            {"id": song[0].strip(), "title": song[1], "duration": song[3]} for song in songs
        ]

        # Return the combined response as JSON
        return jsonify({
            "genre": genre_details,
            "artists": artist_details,
            "albums": album_details,
            "songs": song_details
        })
    else:
        # Return an error if the genre is not found
        return jsonify({"error": "Genre not found"}), 404


# Route for searching playlists
@app.route('/api/search_playlist', methods=['GET'])
@app.route('/api/search_playlist', methods=['GET'])
def api_search_playlist():
    """
    Search for playlists based on a partial or full title match.

    Query Parameters:
        - playlist_title (str): The title (or part of the title) of the playlist to search for.

    Returns:
        - JSON response containing:
            - "playlists": List of playlists that match the search criteria. Each playlist is represented as:
                - "id": Playlist ID.
                - "title": Playlist title.
                - "description": Playlist description.
                - "creationYear": The year the playlist was created.
            - If no title is provided, an empty list is returned.
    """
    # Get the playlist title from the request parameters
    playlist_title = request.args.get('playlist_title')

    # Initialize an empty result list
    if playlist_title:
        # Query to search for playlists with a title matching the input
        query = text("""
                     SELECT * FROM Playlist
                     WHERE Title ILIKE :playlist_title
                     """)
        result = g.conn.execute(query, {'playlist_title': f'%{playlist_title}%'}).fetchall()
    else:
        # No playlist_title provided; return an empty result
        result = []

    # Format the query results into a structured response
    playlists = [
        {
            "id": playlist[0].strip(),
            "title": playlist[1].strip(),
            "description": playlist[2].strip(),
            "creationYear": playlist[3]
        }
        for playlist in result
    ]

    # Return the formatted playlists as a JSON response
    return jsonify({"playlists": playlists})



# Route for displaying playlists.
@app.route('/api/playlist/<playlist_id>', methods=['GET'])
def api_playlist_details(playlist_id):
    """
    Retrieve detailed information about a specific playlist, including its creator, followers, and songs.

    Path Parameters:
        - playlist_id (str): The unique ID of the playlist.

    Returns:
        - JSON response containing:
            - "id": Playlist ID.
            - "title": Playlist title.
            - "description": Playlist description.
            - "creationYear": The year the playlist was created.
            - "creator": Details of the playlist creator, including:
                - "id": User ID of the creator.
                - "name": Username of the creator.
              If no creator exists, returns None.
            - "followers": List of users who follow the playlist. Each follower is represented as:
                - "id": User ID of the follower.
                - "name": Username of the follower.
            - "songs": List of songs in the playlist. Each song is represented as:
                - "id": Song ID.
                - "title": Song title.
                - "duration": Song duration.
        - If the playlist is not found, returns a 404 error with a JSON error message.
    """
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

    # Check if the playlist exists
    if playlist:
        # Format the response data
        playlist_details = {
            "id": playlist[0].strip(),
            "title": playlist[1],
            "description": playlist[2],
            "creationYear": playlist[3],
            "creator": {
                "id": creator[0].strip(),
                "name": creator[1]
            } if creator else None,
            "followers": [
                {"id": follower[0].strip(), "name": follower[1]} for follower in followers
            ],
            "songs": [
                {"id": song[0].strip(), "title": song[1], "duration": song[3]} for song in songs
            ]
        }
        return jsonify(playlist_details)
    else:
        # Return an error if the playlist does not exist
        return jsonify({"error": "Playlist not found"}), 404



# Route for logging in
@app.route('/api/login', methods=['POST'])
def api_login():
    """
    Handle user login by validating the provided username and password.

    Request Body:
        - "username" (str): The user's username (required).
        - "password" (str): The user's password (required).

    Returns:
        - JSON response containing:
            - "success" (bool): Indicates whether the login was successful.
            - "message" (str): A message providing feedback on the login attempt.
            - "username" (str, optional): The username of the logged-in user (only on successful login).

        - HTTP Status Codes:
            - 200: Login successful.
            - 400: Missing username or password in the request body.
            - 401: Invalid username or password.
    """
    # Parse the JSON request body
    data = request.json

    # Extract and validate username and password
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()

    if not username or not password:
        # Return an error if either username or password is missing
        return jsonify({"success": False, "message": "Username or password is missing"}), 400

    # Query the database to validate the user credentials
    user_query = text("SELECT * FROM Users WHERE UserName = :username AND Password = :password")
    user = g.conn.execute(user_query, {'username': username, 'password': password}).fetchone()

    if user:
        # If user is valid, store the username in the session
        session['username'] = username
        return jsonify({"success": True, "message": "Login successful", "username": username}), 200
    else:
        # If user credentials are invalid, return an error
        return jsonify({"success": False, "message": "Invalid username or password"}), 401





# Route for logging out
@app.route('/api/logout', methods=['POST'])
def api_logout():
    """
    Log out the user by clearing their session.

    Returns:
        - JSON response with a success message.
        - HTTP Status Code: 200
    """
    session.pop('username', None)  # Clear the session
    return jsonify({"message": "Logged out successfully"}), 200

# Route for displaying user profile
@app.route('/api/profile/<username>', methods=['GET'])
def api_profile(username):
    """
    Retrieve and display the profile information for a given user.

    Args:
        username (str): The username of the user.

    Returns:
        - JSON response containing:
            - User details (username, email).
            - List of songs the user has listened to.
            - List of artists followed by the user.
            - List of playlists created by the user.
            - List of playlists followed by the user.
        - HTTP Status Code:
            - 200: Profile data retrieved successfully.
            - 404: User not found.
    """
    # Query the user details from the database
    user_query = text("SELECT * FROM Users WHERE UserName = :username")
    user = g.conn.execute(user_query, {'username': username}).fetchone()

    if user:
        # Extract user information based on schema
        username = user[0]  # First column: username
        email = user[1]     # Second column: email
        user_id = user[3]   # Fourth column: userID

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

        # Format and return the response
        return jsonify({
            "user": {"username": username, "email": email},
            "songs": [
                {"id": song[0], "title": song[1], "genre": song[2]}
                for song in songs
            ],
            "artists": [
                {"id": artist[0], "name": artist[1], "followDate": artist[2]}
                for artist in artists
            ],
            "createdPlaylists": [
                {"id": playlist[0], "title": playlist[1]}
                for playlist in created_playlists
            ],
            "followedPlaylists": [
                {"id": playlist[0], "title": playlist[1]}
                for playlist in followed_playlists
            ],
        }), 200
    else:
        # Return an error if the user is not found
        return jsonify({"error": "User not found"}), 404







    

# Route for song recommendations on user profile
@app.route('/api/recommendations/<username>', methods=['GET'])
def api_recommendations(username):
    """
    Generate song recommendations for a user based on their followed genres.

    Args:
        username (str): The username of the user.

    Returns:
        - JSON response containing:
            - List of recommended songs with their details (ID, title, genre, and artist name).
        - HTTP Status Code:
            - 200: Recommendations generated successfully.
            - 404: User not found.
            - 200: No followed genres found.
    """
    # Fetch user ID from the username
    user_query = text("SELECT TRIM(userID) FROM Users WHERE UserName = :username")
    user = g.conn.execute(user_query, {'username': username}).fetchone()

    if not user:
        # Return an error if the user is not found
        return jsonify({"error": "User not found"}), 404

    user_id = user[0]

    # Fetch IDs of songs the user has listened to
    listened_songs_query = text("""
        SELECT TRIM(songID)
        FROM listensTO
        WHERE TRIM(userID) = :user_id
    """)
    listened_song_ids = [
        song[0] for song in g.conn.execute(listened_songs_query, {'user_id': user_id}).fetchall()
    ]

    # Fetch genres followed by the user
    genre_query = text("""
        SELECT DISTINCT TRIM(Genre.Name)
        FROM Artist
        JOIN follows ON TRIM(Artist.ArtistID) = TRIM(follows.ArtistID)
        JOIN belongsTo2 ON TRIM(Artist.ArtistID) = TRIM(belongsTo2.ArtistID)
        JOIN Genre ON TRIM(belongsTo2.GenreID) = TRIM(Genre.GenreID)
        WHERE TRIM(follows.userID) = :user_id
    """)
    followed_genres = [
        genre[0] for genre in g.conn.execute(genre_query, {'user_id': user_id}).fetchall()
    ]

    if not followed_genres:
        # Return a message if the user has no followed genres
        return jsonify({"songs": [], "message": "No followed genres"}), 200

    # Fetch recommended songs based on followed genres
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

    # Format the response with song details
    return jsonify({
        "songs": [
            {"id": song[0], "title": song[1], "genre": song[2], "artist": song[3]}
            for song in recommended_songs
        ]
    }), 200





# Route for the recommended artists button on the user's profile page
@app.route('/recommend_artists/<username>', methods=['GET'])
def recommend_artists(username):
    """
    Generate artist recommendations for a user based on the genres they follow.

    Args:
        username (str): The username of the user.

    Returns:
        - JSON response containing:
            - List of recommended artists with their details (ID, name, biography).
        - HTTP Status Code:
            - 200: Recommendations generated successfully.
            - 200: No followed genres found for the user.
            - 404: User not found in the database.
    """
    # Fetch the user ID based on the provided username
    user_query = text("SELECT userID FROM Users WHERE UserName = :username")
    user = g.conn.execute(user_query, {'username': username}).fetchone()

    if not user:
        # Return an error if the user does not exist
        return jsonify({"error": "User not found"}), 404

    user_id = user[0]

    # Fetch the genres the user follows
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
        # If the user does not follow any genres, return a message
        return jsonify({"message": "No genres found for this user", "artists": []}), 200

    # Initialize a list to store recommended artists
    recommended_artists = []

    # Fetch artists from each genre that the user follows but does not already follow
    for genre in followed_genres:
        genre_id = genre[0].strip()  # Trim any whitespace

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

        # Add the found artists to the recommendations list
        for artist in artists:
            recommended_artists.append({
                "id": artist[0].strip(),  # Artist ID
                "name": artist[1],        # Artist Name
                "biography": artist[2]    # Artist Biography
            })

    # Return the recommended artists as JSON
    return jsonify({"artists": recommended_artists}), 200


# Route for the recommended playlists button on the user's profile page
@app.route('/recommend_playlists/<username>', methods=['GET'])
def recommend_playlists(username):
    """
    Generate playlist recommendations for a user based on the artists they follow.

    Args:
        username (str): The username of the user.

    Returns:
        - JSON response containing:
            - List of recommended playlists with their details (ID, title).
        - HTTP Status Code:
            - 200: Recommendations generated successfully.
            - 200: No followed artists for the user.
            - 404: User not found in the database.
    """
    # Step 1: Fetch the user ID based on the provided username
    user_query = text("SELECT userID FROM Users WHERE UserName = :username")
    user = g.conn.execute(user_query, {'username': username}).fetchone()

    if not user:
        # Return an error if the user does not exist
        return jsonify({"error": "User not found"}), 404

    user_id = user[0]

    # Step 2: Fetch the list of artists followed by the user
    artist_query = text("SELECT ArtistID FROM follows WHERE userID = :user_id")
    followed_artists = g.conn.execute(artist_query, {'user_id': user_id}).fetchall()
    artist_ids = [artist[0] for artist in followed_artists]

    if not artist_ids:
        # If the user does not follow any artists, return a message
        return jsonify({
            "message": "No followed artists, no playlist recommendations available",
            "playlists": []
        }), 200

    # Step 3: Fetch playlists containing songs by the followed artists
    playlist_query = text("""
        SELECT DISTINCT Playlist.PlaylistID, Playlist.Title
        FROM Playlist
        JOIN contains1 ON Playlist.PlaylistID = contains1.PlaylistID
        JOIN contains2 ON contains1.songID = contains2.songID
        JOIN albumBelong ON contains2.AlbumID = albumBelong.AlbumID
        WHERE albumBelong.ArtistID IN :artist_ids
    """)
    playlists = g.conn.execute(playlist_query, {'artist_ids': tuple(artist_ids)}).fetchall()

    # Format the response data
    recommended_playlists = [
        {"id": playlist[0].strip(), "title": playlist[1]} for playlist in playlists
    ]

    return jsonify({"playlists": recommended_playlists}), 200



    

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