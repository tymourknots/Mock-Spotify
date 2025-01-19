import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

function Home() {
  const [songTitle, setSongTitle] = useState('');
  const [albumTitle, setAlbumTitle] = useState('');
  const [artistName, setArtistName] = useState('');
  const [genreName, setGenreName] = useState('');
  const [playlistTitle, setPlaylistTitle] = useState('');
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [username, setUsername] = useState('');
  const navigate = useNavigate();

  // Check login status when the component mounts
  useEffect(() => {
    fetch('http://localhost:8111/api/session', {
      method: 'GET',
      credentials: 'include', // Include cookies for session validation
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.username) {
          setIsLoggedIn(true);
          setUsername(data.username);
        } else {
          setIsLoggedIn(false);
          setUsername('');
        }
      })
      .catch((error) => console.error('Error checking session:', error));
  }, []);
  

  // Handle song search
  const handleSongSearch = (e) => {
    e.preventDefault();
    if (!songTitle.trim()) return;
    navigate(`/search_song?song_title=${encodeURIComponent(songTitle.trim())}`);
  };

  // Handle album search
  const handleAlbumSearch = (e) => {
    e.preventDefault();
    if (!albumTitle.trim()) return;
    navigate(`/search_album?album_title=${encodeURIComponent(albumTitle.trim())}`);
  };

  // Handle artist search
  const handleArtistSearch = (e) => {
    e.preventDefault();
    if (!artistName.trim()) return;
    navigate(`/search_artist?artist_name=${encodeURIComponent(artistName.trim())}`);
  };

  // Handle genre search
  const handleGenreSearch = (e) => {
    e.preventDefault();
    if (!genreName.trim()) return;
    navigate(`/search_genre?genre_name=${encodeURIComponent(genreName.trim())}`);
  };

  // Handle playlist search
  const handlePlaylistSearch = (e) => {
    e.preventDefault();
    if (!playlistTitle.trim()) return;
    navigate(`/search_playlist?playlist_title=${encodeURIComponent(playlistTitle.trim())}`);
  };

  // Handle logout
  const handleLogout = () => {
    fetch('http://localhost:8111/api/logout', {
      method: 'POST',
      credentials: 'include', // Include session cookies
    })
      .then(() => {
        setIsLoggedIn(false);
        setUsername('');
      })
      .catch((error) => console.error('Error logging out:', error));
  };

  return (
    <div>
      <h1>Mock Spotify</h1>
      <div>
        {/* Login/Logout Section */}
        {isLoggedIn ? (
          <div>
            <p>Welcome, {username}!</p>
            <button onClick={() => navigate(`/profile/${username}`)}>Profile</button>
            <button onClick={handleLogout}>Logout</button>
          </div>
        ) : (
          <button onClick={() => navigate('/login')}>Login</button>
        )}
      </div>
      {/* Search Forms */}
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
      <form onSubmit={handleArtistSearch}>
        <p>
          Search for an artist:
          <input
            type="text"
            value={artistName}
            onChange={(e) => setArtistName(e.target.value)}
            placeholder="Search for an artist"
          />
          <button type="submit">Search</button>
        </p>
      </form>
      <form onSubmit={handleGenreSearch}>
        <p>
          Search for a genre:
          <input
            type="text"
            value={genreName}
            onChange={(e) => setGenreName(e.target.value)}
            placeholder="Search for a genre"
          />
          <button type="submit">Search</button>
        </p>
      </form>
      <form onSubmit={handlePlaylistSearch}>
        <p>
          Search for a playlist:
          <input
            type="text"
            value={playlistTitle}
            onChange={(e) => setPlaylistTitle(e.target.value)}
            placeholder="Search for a playlist"
          />
          <button type="submit">Search</button>
        </p>
      </form>
    </div>
  );
}

export default Home;
