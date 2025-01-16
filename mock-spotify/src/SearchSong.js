import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';

function SearchSong() {
  const [songs, setSongs] = useState([]);
  const [playlists, setPlaylists] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [searchParams] = useSearchParams();

  useEffect(() => {
    const songId = searchParams.get('song_id');
    const songTitle = searchParams.get('song_title');

    if (!songId && !songTitle) {
      setSongs([]);
      setPlaylists([]);
      setLoading(false);
      return;
    }

    setLoading(true);
    fetch(
      `http://localhost:8111/api/search_song?${
        songId ? `song_id=${songId}` : `song_title=${encodeURIComponent(songTitle)}`
      }`
    )
      .then((response) => {
        if (!response.ok) {
          throw new Error('No songs found');
        }
        return response.json();
      })
      .then((data) => {
        setSongs(data.songs || []);
        setPlaylists(data.playlists || []);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, [searchParams]);

  if (loading) return <p>Loading...</p>;
  if (error) return <p>{error}</p>;

  return (
    <div>
      <h1>Song Search Results</h1>
      {songs.length > 0 ? (
        songs.map((song) => (
          <div key={song.id}>
            <p>Title: {song.title}</p>
            <p>Album: {song.album.title}</p>
            <p>Artist: {song.artist.name}</p>
            <p>Genre: {song.genre}</p>
            <p>Duration: {song.duration} seconds</p>
          </div>
        ))
      ) : (
        <p>No songs found.</p>
      )}
    </div>
  );
}

export default SearchSong;
