import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

function Home() {
  const [songTitle, setSongTitle] = useState('');
  const [albumTitle, setAlbumTitle] = useState('');
  const navigate = useNavigate();

  const handleSongSearch = (e) => {
    e.preventDefault();
    if (!songTitle.trim()) return;
    navigate(`/search_song?song_title=${encodeURIComponent(songTitle.trim())}`);
  };

  const handleAlbumSearch = (e) => {
    e.preventDefault();
    if (!albumTitle.trim()) return;
    navigate(`/search_album?album_title=${encodeURIComponent(albumTitle.trim())}`);
  };

  return (
    <div>
      <h1>Mock Spotify</h1>
      <form onSubmit={handleSongSearch}>
        <p>
          Search for a song:
          <input
            type="text"
            value={songTitle}
            onChange={(e) => setSongTitle(e.target.value)}
            placeholder="Search for a song"
          />
          <button type="submit">Search</button>
        </p>
      </form>
      <form onSubmit={handleAlbumSearch}>
        <p>
          Search for an album:
          <input
            type="text"
            value={albumTitle}
            onChange={(e) => setAlbumTitle(e.target.value)}
            placeholder="Search for an album"
          />
          <button type="submit">Search</button>
        </p>
      </form>
    </div>
  );
}

export default Home;
