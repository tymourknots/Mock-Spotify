import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';

function AlbumDetails() {
  const { albumId } = useParams(); // Get the album ID from the URL
  const [album, setAlbum] = useState(null);
  const [songs, setSongs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetch(`http://localhost:8111/api/album/${albumId}`)
      .then((response) => {
        if (!response.ok) {
          throw new Error('Album not found');
        }
        return response.json();
      })
      .then((data) => {
        setAlbum(data.album);
        setSongs(data.songs);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, [albumId]);

  if (loading) {
    return <p>Loading album details...</p>;
  }

  if (error) {
    return <p>Error: {error}</p>;
  }

  return (
    <div>
      <h1>Album Details: {album.title}</h1>
      <div>
        <p>Title: {album.title}</p>
        <p>
          Artist: <Link to={`/artist/${album.artistId}`}>{album.artistName}</Link>
        </p>
        <p>Release Year: {album.releaseYear}</p>
        <p>
          Genre: <Link to={`/genre/${album.genreId}`}>{album.genreName}</Link>
        </p>
      </div>

      <h2>Songs in this Album</h2>
      <div>
        {songs.length > 0 ? (
          songs.map((song) => (
            <div key={song.id}>
              <Link to={`/search_song?song_id=${song.id}`}>{song.title}</Link> - Duration: {song.duration} seconds
              console.log(`Navigating to: /search_song?song_id=${song.id}`);

            </div>
          ))
        ) : (
          <p>No songs found in this album.</p>
        )}
      </div>

      <p>
        <Link to="/">Go back to the home page</Link>
      </p>
    </div>
  );
}

export default AlbumDetails;
