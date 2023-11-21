
"""
Columbia's COMS W4111.001 Introduction to Databases
Example Webserver
To run locally:
    python3 server.py
Go to http://localhost:8111 in your browser.
A debugger such as "pdb" may be helpful for debugging.
Read about it online.
"""
import os
  # accessible as a variable in index.html:
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response, abort, session, url_for

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)
app.secret_key = os.urandom(24)

#
# The following is a dummy URI that does not connect to a valid database. You will need to modify it to connect to your Part 2 database in order to use the data.
#
# XXX: The URI should be in the format of:
#
#     postgresql://USER:PASSWORD@34.75.94.195/proj1part2
#
# For example, if you had username gravano and password foobar, then the following line would be:
#
#     DATABASEURI = "postgresql://gravano:foobar@34.75.94.195/proj1part2"
#
DATABASEURI = "postgresql://rz2647:523647@34.74.171.121/proj1part2"


#
# This line creates a database engine that knows how to connect to the URI above.
#
engine = create_engine(DATABASEURI)

#
# Example of running queries in your database
# Note that this will probably not work if you already have a table named 'test' in your database, containing meaningful data. This is only an example showing you how to run queries in your database using SQLAlchemy.
#
conn = engine.connect()

# The string needs to be wrapped around text()

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


#
# @app.route is a decorator around index() that means:
#   run index() whenever the user tries to access the "/" path using a GET request
#
# If you wanted the user to go to, for example, localhost:8111/foobar/ with POST or GET then you could use:
#
#       @app.route("/foobar/", methods=["POST", "GET"])
#
# PROTIP: (the trailing / in the path is important)
#
# see for routing: https://flask.palletsprojects.com/en/2.0.x/quickstart/?highlight=routing
# see for decorators: http://simeonfranklin.com/blog/2012/jul/1/python-decorators-in-12-steps/
#
@app.route('/')
def index():
  """
  request is a special object that Flask provides to access web request information:

  request.method:   "GET" or "POST"
  request.form:     if the browser submitted a form, this contains the data in the form
  request.args:     dictionary of URL arguments, e.g., {a:1, b:2} for http://localhost?a=1&b=2

  See its API: https://flask.palletsprojects.com/en/2.0.x/api/?highlight=incoming%20request%20data

  """

  # DEBUG: this is debugging code to see what request looks like
  print(request.args)


  #
  # example of a database query 
  #
  cursor = g.conn.execute(text("SELECT name FROM test"))
  g.conn.commit()

  # 2 ways to get results

  # Indexing result by column number
  names = []
  for result in cursor:
    names.append(result[0])  

  # Indexing result by column name
  names = []
  results = cursor.mappings().all()
  for result in results:
    names.append(result["name"])
  cursor.close()

  #
  # Flask uses Jinja templates, which is an extension to HTML where you can
  # pass data to a template and dynamically generate HTML based on the data
  # (you can think of it as simple PHP)
  # documentation: https://realpython.com/primer-on-jinja-templating/
  #
  # You can see an example template in templates/index.html
  #
  # context are the variables that are passed to the template.
  # for example, "data" key in the context variable defined below will be
  # accessible as a variable in index.html:
  #
  #     # will print: [u'grace hopper', u'alan turing', u'ada lovelace']
  #     <div>{{data}}</div>
  #
  #     # creates a <div> tag for each element in data
  #     # will print:
  #     #
  #     #   <div>grace hopper</div>
  #     #   <div>alan turing</div>
  #     #   <div>ada lovelace</div>
  #     #
  #     {% for n in data %}
  #     <div>{{n}}</div>
  #     {% endfor %}
  #
  context = dict(data = names)


  #
  # render_template looks in the templates/ folder for files.
  # for example, the below file reads template/index.html
  #
  return render_template("index.html", **context)

#
# This is an example of a different path.  You can see it at:
#
#     localhost:8111/another
#
# Notice that the function name is another() rather than index()
# The functions for each app.route need to have different names
#
@app.route('/another')
def another():
  return render_template("another.html")


# Example of adding new data to the database
@app.route('/add', methods=['POST'])
def add(): 
  name = request.form['name']
  params_dict = {"name":name}
  g.conn.execute(text('INSERT INTO test(name) VALUES (:name)'), params_dict)
  g.conn.commit()
  return redirect('/')

@app.route('/search_song')
def search_song():
    song_title = request.args.get('song_title')
    song_id = request.args.get('song_id')

    result = []
    playlists = []

    if song_id or song_title:
        # Fetch song, album, artist, and genre details
        query = text("""
                    SELECT Song.*, Artist.Name AS ArtistName, Artist.ArtistID, 
                      albumBelong.Title AS AlbumTitle, albumBelong.AlbumID, albumBelong.Genre AS AlbumGenre
                    FROM Song
                    JOIN contains2 ON Song.songID = contains2.songID
                    JOIN albumBelong ON contains2.AlbumID = albumBelong.AlbumID
                    JOIN Artist ON albumBelong.ArtistID = Artist.ArtistID
                    WHERE Song.songID = :song_id OR Song.title = :song_title
                    """)
        result = g.conn.execute(query, {'song_id': song_id, 'song_title': song_title}).fetchall()

        if result and not song_id:
            song_id = result[0][0]  # Extract the song ID from the first result if searching by title

        # Fetch playlists containing the song
        if song_id:
            playlist_query = text("""
                                  SELECT Playlist.* FROM Playlist
                                  JOIN contains1 ON Playlist.PlaylistID = contains1.PlaylistID
                                  WHERE contains1.songID = :song_id
                                  """)
            playlists = g.conn.execute(playlist_query, {'song_id': song_id}).fetchall()

    print("Songs query result:", result)
    print("Playlists containing song:", playlists)
    return render_template("search_song.html", songs=result, playlists=playlists)


@app.route('/search_album')
def search_album():
    album_title = request.args.get('album_title')

    if album_title:
        query = text("""
                     SELECT albumBelong.*, Artist.Name AS ArtistName
                     FROM albumBelong
                     JOIN Artist ON albumBelong.ArtistID = Artist.ArtistID
                     WHERE Title = :album_title
                     """)
        result = g.conn.execute(query, {'album_title': album_title}).fetchall()
    else:
        result = []

    print("Albums query result:", result)
    return render_template("search_album.html", albums=result)


@app.route('/album/<album_id>')
def album_details(album_id):
    album_query = text("""
                     SELECT albumBelong.*, Artist.Name AS ArtistName, Artist.ArtistID, Genre.Name AS GenreName
                     FROM albumBelong
                     JOIN Artist ON albumBelong.ArtistID = Artist.ArtistID
                     JOIN belongsTo2 ON Artist.ArtistID = belongsTo2.ArtistID
                     JOIN Genre ON belongsTo2.GenreID = Genre.GenreID
                     WHERE albumBelong.AlbumID = :album_id
                     """)
    album_details = g.conn.execute(album_query, {'album_id': album_id}).fetchone()

    # Fetch songs in the album
    songs_query = text("""
                       SELECT song.* FROM song
                       JOIN contains2 ON song.songID = contains2.songID
                       WHERE contains2.AlbumID = :album_id
                       """)
    songs = g.conn.execute(songs_query, {'album_id': album_id}).fetchall()

    print("Album details:", album_details)
    print("Songs in album:", songs)
    if album_details:
        return render_template('album_details.html', album=album_details, songs=songs)
    else:
        return "Album not found", 404

@app.route('/search_artist')
def search_artist():
    artist_name = request.args.get('artist_name')

    if artist_name:
        query = text("""
                     SELECT * FROM Artist WHERE Name LIKE :artist_name
                     """)
        result = g.conn.execute(query, {'artist_name': f'%{artist_name}%'}).fetchall()
    else:
        result = []

    print("Artists query result:", result)
    return render_template('search_artist.html', artists=result)


@app.route('/artist/<artist_id>')
def artist_details(artist_id):
  artist_query = text("""
                      SELECT Artist.*, Genre.Name AS GenreName, Genre.GenreID
                      FROM Artist
                      JOIN belongsTo2 ON Artist.ArtistID = belongsTo2.ArtistID
                      JOIN Genre ON belongsTo2.GenreID = Genre.GenreID
                      WHERE Artist.ArtistID = :artist_id
                      """)
  artist_details = g.conn.execute(artist_query, {'artist_id': artist_id}).fetchone()
  print("Artist details:", artist_details)

  albums_query = text("""
                      SELECT * FROM albumBelong WHERE ArtistID = :artist_id
                      """)
  albums = g.conn.execute(albums_query, {'artist_id': artist_id}).fetchall()

  songs_query = text("""
                    SELECT Song.* FROM Song
                    JOIN contains2 ON Song.songID = contains2.songID
                    JOIN albumBelong ON contains2.AlbumID = albumBelong.AlbumID
                    WHERE albumBelong.ArtistID = :artist_id
                    """)
  songs = g.conn.execute(songs_query, {'artist_id': artist_id}).fetchall()
  print("Songs by artist:", songs)

  return render_template('artist_details.html', artist=artist_details, albums=albums, songs=songs)


@app.route('/search_genre')
def search_genre():
    genre_name = request.args.get('genre_name')

    if genre_name:
        query = text("""
                     SELECT * FROM Genre
                     WHERE Name ILIKE :genre_name
                     """)
        result = g.conn.execute(query, {'genre_name': f'%{genre_name}%'}).fetchall()
    else:
        result = []

    print("Genres query result:", result)
    return render_template("search_genre.html", genres=result)

@app.route('/search_g/<genre_name>')
def search_g(genre_name):
    # Adjusted query to join Song with albumBelong indirectly
    query = text("""
                 SELECT Song.* FROM Song
                 JOIN contains2 ON Song.songID = contains2.songID
                 JOIN albumBelong ON contains2.AlbumID = albumBelong.AlbumID
                 WHERE albumBelong.Genre ILIKE :genre_name
                 """)
    songs = g.conn.execute(query, {'genre_name': f'%{genre_name}%'}).fetchall()

    if songs:
        return render_template('genre.html', genre=genre_name, songs=songs)
    else:
        return f"No songs found for genre: {genre_name}", 404




@app.route('/genre/<genre_id>')
def genre_details(genre_id):
  genre_query = text("""
                     SELECT * FROM Genre WHERE GenreID = :genre_id
                      """)
  genre_details = g.conn.execute(genre_query, {'genre_id': genre_id}).fetchone()

  artists_query = text("""
                        SELECT Artist.* FROM Artist
                        JOIN belongsTo2 ON Artist.ArtistID = belongsTo2.ArtistID
                        WHERE belongsTo2.GenreID = :genre_id
                        """)
  artists = g.conn.execute(artists_query, {'genre_id': genre_id}).fetchall()

  albums_query = text("""
                      SELECT albumBelong.* FROM albumBelong
                      WHERE albumBelong.Genre = (SELECT Name FROM Genre WHERE GenreID = :genre_id)
                      """)
  albums = g.conn.execute(albums_query, {'genre_id': genre_id}).fetchall()
  return render_template('genre_details.html', genre = genre_details, artists= artists, albums = albums)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password'].strip()

        user_query = text("SELECT * FROM Users WHERE UserName = :username AND Password = :password")
        user = g.conn.execute(user_query, {'username': username, 'password': password}).fetchone()

        if user:
            session['username'] = username  
            return redirect(url_for('index'))
        else:
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)  # Remove the username from the session
    return redirect(url_for('index'))

@app.route('/profile/<username>')
def profile(username):
    if 'username' in session and session['username'] == username:
        user_query = text("SELECT * FROM Users WHERE UserName = :username")
        user = g.conn.execute(user_query, {'username': username}).fetchone()

        if user:
            # Fetch the list of songs the user listens to
            listens_to_query = text("""
                                   SELECT Song.* FROM Song
                                   JOIN ListensTo ON Song.songID = ListensTo.songID
                                   WHERE ListensTo.userID = :user_id
                                   """)
            listened_songs = g.conn.execute(listens_to_query, {'user_id': user[0]}).fetchall()  

            followed_artists_query = text("""
                                          SELECT Artist.*, Follows.FollowDate
                                          FROM Follows
                                          JOIN Artist ON Follows.ArtistID = Artist.ArtistID
                                          WHERE Follows.userID = :user_id
                                          """)
            followed_artists = g.conn.execute(followed_artists_query, {'user_id': user[0]}).fetchall()

            created_playlists_query = text("""
                                           SELECT Playlist.* FROM Playlist
                                           JOIN CreateORFollow ON Playlist.PlaylistID = CreateORFollow.PlaylistID
                                           WHERE CreateORFollow.userID = :user_id AND CreateORFollow.Creates = TRUE
                                            """)
            created_playlists = g.conn.execute(created_playlists_query, {'user_id': user[0]}).fetchall()

            followed_playlists_query = text("""
                                            SELECT Playlist.* FROM Playlist
                                            JOIN CreateORFollow ON Playlist.PlaylistID = CreateORFollow.PlaylistID
                                            WHERE CreateORFollow.userID = :user_id AND CreateORFollow.Creates = FALSE
                                            """)
            followed_playlists = g.conn.execute(followed_playlists_query, {'user_id': user[0]}).fetchall()

            user_id = user[0]

            return render_template('profile.html', user=user, songs=listened_songs, artists=followed_artists, created_playlists=created_playlists, followed_playlists=followed_playlists)
        else:
            return "User not found", 404
    else:
        return redirect(url_for('login'))
    

@app.route('/recommendations/<user_id>')
def recommendations(user_id):
    # Step 1: Find the artists the user follows
    artist_query = text("SELECT ArtistID FROM Follows WHERE userID = :user_id")
    followed_artists = g.conn.execute(artist_query, {'user_id': user_id}).fetchall()

    # Step 2: Select songs and artist names from these artists
    recommended_songs = []
    for artist in followed_artists:
        song_query = text("""
                          SELECT Song.*, Artist.Name AS ArtistName, Artist.ArtistID 
                          FROM Song
                          JOIN contains2 ON Song.songID = contains2.songID
                          JOIN albumBelong ON contains2.AlbumID = albumBelong.AlbumID
                          JOIN Artist ON albumBelong.ArtistID = Artist.ArtistID
                          WHERE Artist.ArtistID = :artist_id
                          ORDER BY RANDOM() LIMIT 5
                          """)
        songs = g.conn.execute(song_query, {'artist_id': artist[0]}).fetchall()
        recommended_songs.extend(songs)

    # Step 3: Present recommendations to the user
    return render_template('recommendations.html', songs=recommended_songs)

@app.route('/recommend_artists/<user_id>')
def recommend_artists(user_id):
    # Fetch genres of artists the user follows
    genre_query = text("""
                       SELECT DISTINCT Genre.GenreID
                       FROM Artist
                       JOIN Follows ON Artist.ArtistID = Follows.ArtistID
                       JOIN belongsTo2 ON Artist.ArtistID = belongsTo2.ArtistID
                       JOIN Genre ON belongsTo2.GenreID = Genre.GenreID
                       WHERE Follows.userID = :user_id
                       """)
    followed_genres = g.conn.execute(genre_query, {'user_id': user_id}).fetchall()

    # Fetch artists in those genres that the user does not follow
    recommended_artists = []
    for genre in followed_genres:
        artist_query = text("""
                            SELECT Artist.*
                            FROM Artist
                            JOIN belongsTo2 ON Artist.ArtistID = belongsTo2.ArtistID
                            WHERE belongsTo2.GenreID = :genre_id
                            AND Artist.ArtistID NOT IN (
                                SELECT ArtistID FROM Follows WHERE userID = :user_id
                            )
                            LIMIT 5
                            """)
        artists = g.conn.execute(artist_query, {'genre_id': genre[0], 'user_id': user_id}).fetchall()
        recommended_artists.extend(artists)

    return render_template('recommend_artists.html', artists=recommended_artists)

@app.route('/recommend_playlists/<user_id>')
def recommend_playlists(user_id):
    # Step 1: Fetch the artists followed by the user
    artist_query = text("SELECT ArtistID FROM Follows WHERE userID = :user_id")
    followed_artists = g.conn.execute(artist_query, {'user_id': user_id}).fetchall()

    # Convert followed artists to a list of artist IDs
    artist_ids = [artist[0] for artist in followed_artists]

    if not artist_ids:
        return "No artists followed, so no playlist recommendations available."

    # Step 2: Fetch playlists that contain songs by these artists
    playlist_query = text("""
        SELECT DISTINCT Playlist.PlaylistID, Playlist.Title
        FROM Playlist
        JOIN contains1 ON Playlist.PlaylistID = contains1.PlaylistID
        JOIN contains2 ON contains1.songID = contains2.songID
        JOIN albumBelong ON contains2.AlbumID = albumBelong.AlbumID
        WHERE albumBelong.ArtistID IN :artist_ids
    """)
    playlists = g.conn.execute(playlist_query, {'artist_ids': tuple(artist_ids)}).fetchall()

    # Step 3: Present the recommended playlists to the user
    return render_template('recommend_playlists.html', playlists=playlists)




@app.route('/search_playlist')
def search_playlist():
    playlist_title = request.args.get('playlist_title')

    if playlist_title:
        query = text("""
                     SELECT * FROM Playlist
                     WHERE Title ILIKE :playlist_title
                     """)
        result = g.conn.execute(query, {'playlist_title': f'%{playlist_title}%'}).fetchall()
    else:
        result = []

    print("Playlists query result:", result)
    return render_template("search_playlist.html", playlists=result)


@app.route('/playlist/<playlist_id>')
def playlist_details(playlist_id):
    playlist_query = text("""
                          SELECT * FROM Playlist
                          WHERE PlaylistID = :playlist_id
                          """)
    playlist = g.conn.execute(playlist_query, {'playlist_id': playlist_id}).fetchone()
    print("Playlist ID:", playlist_id)
    print("Playlist query result:", playlist)

    # Fetch songs in the playlist
    songs_query = text("""
                       SELECT Song.* FROM Song
                       JOIN contains1 ON Song.songID = contains1.songID
                       WHERE contains1.PlaylistID = :playlist_id
                       """)
    songs = g.conn.execute(songs_query, {'playlist_id': playlist_id}).fetchall()

    creator_query = text("""
                         SELECT Users.* FROM Users
                         JOIN CreateORFollow ON Users.UserID = CreateORFollow.UserID
                         WHERE CreateORFollow.PlaylistID = :playlist_id AND CreateORFollow.Creates = TRUE
                         """)
    creator = g.conn.execute(creator_query, {'playlist_id': playlist_id}).fetchone()

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
