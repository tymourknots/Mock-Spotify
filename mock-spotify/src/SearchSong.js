import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';

function SearchSong() {
  const [songs, setSongs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchParams] = useSearchParams();

  useEffect(() => {
    const songTitle = searchParams.get('song_title');
    if (!songTitle) {
      setSongs([]);
      setLoading(false);
      return;
    }

    setLoading(true);
    fetch(`http://localhost:8111/api/search_song?song_title=${encodeURIComponent(songTitle)}`)
      .then((response) => response.json())
      .then((data) => {
        setSongs(data.songs || []);
        setLoading(false);
      })
      .catch((error) => {
        console.error('Error fetching song data:', error);
        setLoading(false);
      });
  }, [searchParams]);

  if (loading) {
    return <p>Loading...</p>;
  }

  return (
    <div>
      <h1>Song Search Results</h1>
      {songs.length > 0 ? (
        songs.map((song) => (
          <div key={song.id}>
            <p>Title: {song.title}</p>
            <p>
              Album: <a href={`/album/${song.album.id}`}>{song.album.title}</a>
            </p>
            <p>
              Artist: <a href={`/artist/${song.artist.id}`}>{song.artist.name}</a>
            </p>
            <p>Genre: {song.genre}</p>
            <p>Release Year: {song.releaseYear}</p>
            <p>Plays: {song.plays}</p>
          </div>
        ))
      ) : (
        <p>No songs found.</p>
      )}
    </div>
  );
}

export default SearchSong;
