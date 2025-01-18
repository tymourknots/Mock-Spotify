import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';

function GenreDetails() {
  const { genreId } = useParams(); // Get genre ID from URL
  const [genre, setGenre] = useState(null);
  const [artists, setArtists] = useState([]);
  const [albums, setAlbums] = useState([]);
  const [songs, setSongs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetch(`http://localhost:8111/api/genre/${genreId}`)
      .then((response) => {
        if (!response.ok) {
          throw new Error('Genre not found');
        }
        return response.json();
      })
      .then((data) => {
        setGenre(data.genre);
        setArtists(data.artists);
        setAlbums(data.albums);
        setSongs(data.songs);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, [genreId]);

  if (loading) return <p>Loading genre details...</p>;
  if (error) return <p>{error}</p>;

  return (
    <div>
      <h1>Genre Details: {genre.name}</h1>
      <div>
        <p>Name: {genre.name}</p>
        <p>Description: {genre.description}</p>
      </div>

      <h2>Artists in this Genre</h2>
      <div>
        {artists.length > 0 ? (
          artists.map((artist) => (
            <div key={artist.id}>
              <Link to={`/artist/${artist.id}`}>{artist.name}</Link>
            </div>
          ))
        ) : (
          <p>No artists found in this genre.</p>
        )}
      </div>

      <h2>Albums in this Genre</h2>
      <div>
        {albums.length > 0 ? (
          albums.map((album) => (
            <div key={album.id}>
              <Link to={`/album/${album.id}`}>{album.title}</Link>
            </div>
          ))
        ) : (
          <p>No albums found in this genre.</p>
        )}
      </div>

      <h2>Songs in this Genre</h2>
      <div>
        {songs.length > 0 ? (
          songs.map((song) => (
            <div key={song.id}>
              <Link to={`/search_song?song_id=${song.id}`}>{song.title}</Link> - Duration: {song.duration} seconds
            </div>
          ))
        ) : (
          <p>No songs found in this genre.</p>
        )}
      </div>

      <p>
        <Link to="/">Go back to the home page</Link>
      </p>
    </div>
  );
}

export default GenreDetails;
