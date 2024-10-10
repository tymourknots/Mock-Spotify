UPDATES PENDING: will implement React and CSS into the project in the near future

Tymour Aidabole (taa2146)
Ranjing Zhang (rz2647)
1.) PostgreSQL account
    Username: rz2647 (psql -U rz2647 -h 34.74.171.121 -d proj1part2)
    Password: 523647

2.) http://35.230.170.215:8111/

3.) We were able to create most of the functionality proposed in Part 1, in our application. The application can search for all the entities as described, and each entity
page has links to the other entities it has relationships with (both directly and indirectly). Finding a song will have a link to the artist of the song, album the song belongs to, 
the genre the song belongs to, as well as any playlists it belongs to. We took out the ability to see which other users follow an artist, as well as the ability to even view other
user's profiles, as those features aren't on Spotify and seemed redundant to include. We also took out the ability to show the user which songs they have liked or which songs had been liked
by which users, because the SQL schema had no connections/relationships between the User and Liked Songs; Liked Songs was just an arbitrary attribute in Songs, so it didn't make sense to annotate a non-existent relationship. 
We implemented a new feature of a login system. The user can choose to Login at the homepage, which creates a unique session if the correct User/Password combo is inputted. Once logged in, the user can
view their profile which shows their user information, songs they listened to, artists they follow, playlists they've created or followed, as well as three recommendation buttons- one to recommend songs,
one to recommend artists, and one to recommend playlists, all of which are run by a recommendation algorithm based on the artists that the user follows. The recommendation algorithm was a part of the Part 1 proposal, but the
login function was not, and is a brand new feature. However, the recommendation algorithm is a little more rudimentary than what was originally proposed. It makes recommendations based only on the artists the user follows, and not their previous 
listening experience, their liked songs, or their playlists. Recommending based on all of those attributes would require a lot more complexity and a lot more data to work efficiently, so I chose to simplify and only use the artists followed. 

4.) The recommended songs button and the URL links between Songs and Genres pages are the two most interesting database operations of our project. 
The recommendation buttons are all based on the artists that a user follows. There are three recommendation types: a song, an artist, or a playlist. Recommending artists and playlists was fairly simple; for artists, we just found the genres that the artists-followed belonged to
and recommended other artists of that genre and for playlists, we just found all the playlists that the artists-followed belonged to and recommended those playlists. Songs is where things got tricky, as there actually is no direct relationship between Songs and Artists in our SQL schema 
from part 2 (bad design choice in hindsight). So to make it work, we had to do a bit of manipulation via SQL querying. For songs, we took the artists-followed, used a SQL query to join the artists with the albums that belong to them, then joined the songs with the corresponding
albums, and finally joined them all together to create an indirect connection between songs and artists that actually works by jumping from Songs -> Albums -> Artists. Finally, the algorithm then uses this indirect connection to recommend all songs by the artist-followed.

The URL links between Songs and Genres is also interesting because it is also an indirect connection between the song and genre entitites. It works similarly to the recommended songs button in that it also uses SQL querying to manipulate a connection 
between two entities that are otherwise totally unrelated. This is because the GenreID found in the Songs table is arbitrary and not directly linked with any GenreID's in the Genre table as a relationship(another bad design choice from part 2 in hindsight).
It uses querying to join together songs and their respective albums, then replaces the arbitrary GenreID in Songs with the GenreID found in the album and creates a link between the two. We chose to use the album genre to replace GenreID in Songs because we wanted to give 
the artists room to produce albums that may be outside of their respective genres. What if Taylor Swift decided to become a metalhead or rapper in her latest album? We wanted to keep that possibility open, so we prioritized the album genre. 

5.) We did not use any AI tools for the project. 
