import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';

function ArtistDetails() {
  const { artistId } = useParams(); // Get artist ID from URL
  const [artist, setArtist] = useState(null);
  const [albums, setAlbums] = useState([]);
  const [songs, setSongs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetch(`http://localhost:8111/api/artist/${artistId}`)
      .then((response) => {
        if (!response.ok) {
          throw new Error('Artist not found');
        }
        return response.json();
      })
      .then((data) => {
        setArtist(data.artist);
        setAlbums(data.albums);
        setSongs(data.songs);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, [artistId]);

  if (loading) return <p>Loading artist details...</p>;
  if (error) return <p>{error}</p>;

  return (
    <div>
      <h1>Artist Details: {artist.name}</h1>
      <div>
        <p>Name: {artist.name}</p>
        <p>Biography: {artist.biography}</p>
        <p>
          Genre: <Link to={`/genre/${artist.genreId}`}>{artist.genreName}</Link>
        </p>
      </div>

      <h2>Albums by this Artist</h2>
      <div>
        {albums.length > 0 ? (
          albums.map((album) => (
            <div key={album.id}>
              <Link to={`/album/${album.id}`}>{album.title}</Link> - Release Year: {album.releaseYear}
            </div>
          ))
        ) : (
          <p>No albums found for this artist.</p>
        )}
      </div>

      <h2>Songs by this Artist</h2>
      <div>
        {songs.length > 0 ? (
          songs.map((song) => (
            <div key={song.id}>
              <Link to={`/search_song?song_id=${song.id}`}>{song.title}</Link> - Genre: {song.genre}
            </div>
          ))
        ) : (
          <p>No songs found for this artist.</p>
        )}
      </div>

      <p>
        <Link to="/">Go back to the home page</Link>
      </p>
    </div>
  );
}

export default ArtistDetails;
